import axios from 'axios';
import { message } from 'ant-design-vue';
import router from '../router';

// 创建 axios 实例
const service = axios.create({
  baseURL: '', // 使用代理，所以留空或 /api
  timeout: 10000,
  withCredentials: true // 跨域请求时发送 cookies
});

// 是否正在刷新 token 的标记
let isRefreshing = false;
// 重试队列，每一项将是一个待执行的函数形式
let requests = [];

// 请求拦截器
service.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    console.log(error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data;
    
    // 如果返回的 code 不是 0，则判断为错误
    if (res.code !== 0 && res.code !== 200) {
      // 错误码处理
      // 2002: Token已过期
      // 2004: Session已过期
      if (res.code === 2002 || res.code === 2004) {
        if (!isRefreshing) {
          isRefreshing = true;
          // 尝试刷新 session/token
          // 注意：如果您的后端刷新接口也是基于 session cookie，则直接调用刷新接口
          return service.post('/api/v1/auth/token/refresh')
            .then(res => {
              if (res.code === 0) {
                // 刷新成功，执行队列中的请求
                requests.forEach(cb => cb());
                requests = [];
                // 重试当前请求
                return service(response.config);
              } else {
                // 刷新失败，抛出错误进入 catch
                throw new Error('Token refresh failed');
              }
            })
            .catch(() => {
              // 刷新失败或出错，清除用户信息并跳转登录
              localStorage.removeItem('userInfo');
              localStorage.removeItem('token');
              router.push('/login');
              requests = [];
              return Promise.reject(new Error('会话已过期，请重新登录'));
            })
            .finally(() => {
              isRefreshing = false;
            });
        } else {
          // 正在刷新中，将请求加入队列
          return new Promise(resolve => {
            requests.push(() => {
              resolve(service(response.config));
            });
          });
        }
      }
      
      // 2001: 未授权
      // 2003: Token无效
      // 2005: Session无效
      // 4005: 权限不足
      if ([2001, 2003, 2005, 4005].includes(res.code)) {
        localStorage.removeItem('userInfo');
        localStorage.removeItem('token');
        router.push('/login');
        const errorMsgMap = {
          2001: '未授权，请登录',
          2003: 'Token无效，请重新登录',
          2005: 'Session无效，请重新登录',
          4005: '权限不足'
        };
        const errorMsg = errorMsgMap[res.code] || res.message || 'Error';
        // Token 相关错误不弹出提示，直接跳转登录；仅权限不足时给出提示
        if (res.code === 4005) {
          message.error(errorMsg);
        }
        return Promise.reject(new Error(errorMsg));
      }
      
      // 其他业务错误直接提示
      // 1003: 禁止访问
      // 3001: 用户不存在
      // 3002: 用户已存在
      // 3003: 密码错误
      // 3006: 验证码错误
      // 3008: 用户已禁用
      // 4001: 管理员不存在
      // 4002: 管理员已存在
      // 4003: 管理员密码错误
      // 4004: 管理员已禁用
      const errorMsg = {
          1003: '禁止访问',
          3001: '用户不存在',
          3002: '用户已存在',
          3003: '密码错误',
          3006: '验证码错误',
          3008: '用户已禁用',
          4001: '管理员不存在',
          4002: '管理员已存在',
          4003: '管理员密码错误',
          4004: '管理员已禁用'
      }[res.code] || res.message || 'Error';
      
      message.error(errorMsg);
      return Promise.reject(new Error(errorMsg));
    } else {
      return res;
    }
  },
  error => {
    // console.log('err' + error);
    
    // 如果是刷新 token 请求本身失败 (无论是 401 还是 422 等其他错误)，直接登出
    if (error.config && error.config.url.includes('/auth/token/refresh')) {
      localStorage.removeItem('userInfo');
      localStorage.removeItem('token');
      router.push('/login');
      return Promise.reject(error);
    }

    // 处理 HTTP 状态码为 401 的情况 (Session 过期)
    if (error.response && error.response.status === 401) {

      if (!isRefreshing) {
        isRefreshing = true;
        return service.post('/api/v1/auth/token/refresh')
          .then(res => {
            if (res.code === 0) {
              // 刷新成功，执行队列中的请求
              requests.forEach(cb => cb());
              requests = [];
              // 重试当前请求
              return service(error.config);
            } else {
              throw new Error('Token refresh failed');
            }
          })
          .catch(() => {
            localStorage.removeItem('userInfo');
            localStorage.removeItem('token');
            router.push('/login');
            requests = [];
            return Promise.reject(error);
          })
          .finally(() => {
            isRefreshing = false;
          });
      } else {
        return new Promise(resolve => {
          requests.push(() => {
            resolve(service(error.config));
          });
        });
      }
    }
    
    // 处理 403 无权限/Token无效
    if (error.response && error.response.status === 403) {
      localStorage.removeItem('userInfo');
      localStorage.removeItem('token');
      router.push('/login');
      return Promise.reject(error);
    }
    
    message.error(error.message || '请求失败');
    return Promise.reject(error);
  }
);

export default service;
