import request from '../utils/request';

/**
 * 管理员手机号注册
 * @param {Object} data { phone, password, username, verify_code }
 */
export function registerByPhone(data) {
  return request({
    url: '/api/v1/admin/register/phone',
    method: 'post',
    data
  });
}

/**
 * 管理员邮箱注册
 * @param {Object} data { email, password, username, verify_code }
 */
export function registerByEmail(data) {
  return request({
    url: '/api/v1/admin/register/email',
    method: 'post',
    data
  });
}

/**
 * 兼容旧注册接口（默认使用邮箱注册，适配现有代码）
 * @param {Object} data 
 */
export function register(data) {
  if (data.phone) {
    return registerByPhone(data);
  }
  return registerByEmail(data);
}

/**
 * 管理员密码登录
 * @param {Object} data { account, password }
 */
export function login(data) {
  return request({
    url: '/api/v1/admin/login/password',
    method: 'post',
    data
  });
}

/**
 * 管理员验证码登录
 * @param {Object} data { account, verify_code }
 */
export function loginByVerificationCode(data) {
  return request({
    url: '/api/v1/admin/login/verify-code',
    method: 'post',
    data
  });
}

/**
 * 管理员登出
 */
export function logout() {
  return request({
    url: '/api/v1/admin/logout',
    method: 'post'
  });
}

/**
 * 获取当前管理员信息
 */
export function getCurrentAdmin() {
  return request({
    url: '/api/v1/admin/me',
    method: 'get'
  });
}

/**
 * 更新当前管理员信息
 * @param {Object} data { name, phone, email }
 */
export function updateCurrentAdmin(data) {
  return request({
    url: '/api/v1/admin/me',
    method: 'put',
    data
  });
}

/**
 * 修改密码
 * @param {Object} data { old_password, new_password }
 */
export function updatePassword(data) {
  return request({
    url: '/api/v1/admin/me/password',
    method: 'post',
    data
  });
}

/**
 * 发送验证码
 * @param {Object} data { target, scene }
 */
export function sendVerificationCode(data) {
  return request({
    url: '/api/v1/auth/verify-code/send',
    method: 'post',
    data
  });
}

/**
 * 刷新 Session
 */
export function refreshToken() {
  return request({
    url: '/api/v1/auth/token/refresh',
    method: 'post'
  });
}
