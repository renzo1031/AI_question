const config = require('./config.js');

class Request {
  constructor() {
    this.isRefreshing = false;
    this.subscribers = []; // 重试队列
  }

  /**
   * 统一请求方法
   * @param {Object} options 请求配置
   */
  request(options) {
    const { url, method = 'GET', data, header = {} } = options;
    const fullUrl = url.startsWith('http') ? url : config.baseUrl + url;
    
    // 主动检查 Token 是否即将过期（提前 1 分钟）
    // 排除登录和刷新接口
    if (!url.includes('auth/login') && !url.includes('auth/token/refresh')) {
      const expireTime = wx.getStorageSync(config.tokenExpireKey);
      const now = Date.now();
      
      // 如果有过期时间，且当前时间距离过期小于 60000 毫秒 (1分钟)
      // 或者已经过期
      if (expireTime && (expireTime - now < 60000)) {
        return new Promise((resolve, reject) => {
          this._handleTokenRefresh(options, resolve, reject);
        });
      }
    }

    // 构造请求头
    const finalHeader = this._getHeaders(url, header);

    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        method: method.toUpperCase(),
        data,
        header: finalHeader,
        success: (res) => this._handleResponse(res, options, resolve, reject),
        fail: (err) => this._handleFail(err, reject)
      });
    });
  }

  /**
   * 构造请求头
   */
  _getHeaders(url, customHeader) {
    const header = {
      'Content-Type': 'application/json',
      ...customHeader
    };

    // 排除刷新 Token 接口，其他接口自动携带 Token
    if (!url.includes('auth/token/refresh')) {
      const token = wx.getStorageSync(config.tokenKey);
      if (token) {
        header['Authorization'] = `Bearer ${token}`;
      }
    }
    return header;
  }

  /**
   * 处理响应
   */
  _handleResponse(res, options, resolve, reject) {
    const { statusCode, data } = res;

    // 1. HTTP 成功 (200-299)
    if (statusCode >= 200 && statusCode < 300) {
      // 1.1 业务成功
      if (data.code === 0) {
        // 返回处理后的数据（兼容分页）
        if (data.page_info || data.total !== undefined || data.total_count !== undefined) {
          return resolve(data);
        }
        return resolve(data.data);
      }
      
      // 1.2 Token 相关错误 (2001, 2002, 2003)
      // 2001: 未授权, 2002: Token已过期, 2003: Token无效
      if ([2001, 2002, 2003].includes(data.code)) {
        if (!options.url.includes('auth/login')) {
           return this._handleTokenRefresh(options, resolve, reject);
        }
      }

      // 1.3 其他业务错误
      const msg = data.message || '请求失败';
      this._showError(msg);
      return reject(data);
    }

    // 2. HTTP 401 未授权
    if (statusCode === 401) {
       if (!options.url.includes('auth/login')) {
         return this._handleTokenRefresh(options, resolve, reject);
       } else {
         const msg = (data && data.message) ? data.message : '未授权';
         this._showError(msg);
         return reject(data || res);
       }
    }

    // 3. 其他 HTTP 错误
    const msg = (data && data.message) ? data.message : `请求失败(${statusCode})`;
    this._showError(msg);
    reject(res);
  }

  /**
   * 处理 Token 刷新
   */
  _handleTokenRefresh(options, resolve, reject) {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      const refreshToken = wx.getStorageSync(config.refreshTokenKey);

      if (!refreshToken) {
        this._redirectToLogin();
        this.isRefreshing = false;
        return reject({ message: '请重新登录' });
      }

      // 发起刷新请求
      wx.request({
        url: config.baseUrl + '/auth/token/refresh',
        method: 'POST',
        data: { refresh_token: refreshToken },
        success: (res) => {
          if (res.statusCode === 200 && res.data.code === 0) {
            const { access_token, refresh_token, accessExpireAt } = res.data.data;
            wx.setStorageSync(config.tokenKey, access_token);
            if (refresh_token) {
              wx.setStorageSync(config.refreshTokenKey, refresh_token);
            }
            if (accessExpireAt) {
              wx.setStorageSync(config.tokenExpireKey, accessExpireAt);
            }
            
            // 执行队列
            this.subscribers.forEach(cb => cb());
            this.subscribers = [];
            
            // 重试当前请求
            this.request(options).then(resolve).catch(reject);
          } else {
            this._redirectToLogin();
            const msg = (res.data && res.data.message) || '登录已过期，请重新登录';
            this._showError(msg);
            reject(res.data);
          }
        },
        fail: () => {
          this._redirectToLogin();
          reject({ message: '网络错误' });
        },
        complete: () => {
          this.isRefreshing = false;
        }
      });
    } else {
      // 加入队列
      this.subscribers.push(() => {
        this.request(options).then(resolve).catch(reject);
      });
    }
  }

  /**
   * 处理网络失败
   */
  _handleFail(err, reject) {
    this._showError('连接失败');
    reject(err);
  }

  /**
   * 显示错误
   */
  _showError(msg) {
    wx.showToast({
      title: msg || '请求失败',
      icon: 'none'
    });
  }

  /**
   * 跳转登录
   */
  _redirectToLogin() {
    wx.removeStorageSync(config.tokenKey);
    wx.removeStorageSync(config.refreshTokenKey);
    wx.removeStorageSync(config.userKey);

    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    const ignoreRoutes = ['pages/auth/login', 'pages/auth/register'];
    
    if (currentPage && !ignoreRoutes.includes(currentPage.route)) {
      wx.reLaunch({ url: '/pages/auth/login' });
    }
  }

  // 快捷方法
  get(url, data, header) { return this.request({ url, method: 'GET', data, header }); }
  post(url, data, header) { return this.request({ url, method: 'POST', data, header }); }
  put(url, data, header) { return this.request({ url, method: 'PUT', data, header }); }
  del(url, data, header) { return this.request({ url, method: 'DELETE', data, header }); }
}

const requestInstance = new Request();

module.exports = {
  request: requestInstance.request.bind(requestInstance),
  get: requestInstance.get.bind(requestInstance),
  post: requestInstance.post.bind(requestInstance),
  put: requestInstance.put.bind(requestInstance),
  del: requestInstance.del.bind(requestInstance)
};
