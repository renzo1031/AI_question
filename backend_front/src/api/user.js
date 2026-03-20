import request from '../utils/request';

/**
 * 获取用户列表
 * @param {Object} params { page, page_size, keyword, status, created_from, created_to, last_login_from, last_login_to }
 */
export function getUserList(params) {
  return request({
    url: '/api/v1/admin/users/list',
    method: 'get',
    params
  });
}

/**
 * 获取用户详细信息
 * @param {string} userId
 */
export function getUserDetail(userId) {
  return request({
    url: `/api/v1/admin/users/${userId}`,
    method: 'get'
  });
}

/**
 * 更新用户状态
 * @param {string} userId
 * @param {string} status 'active' | 'disabled'
 * @param {string} disabledReason
 */
export function updateUserStatus(userId, status, disabledReason) {
  return request({
    url: `/api/v1/admin/users/${userId}/status`,
    method: 'put',
    data: { status, disabled_reason: disabledReason }
  });
}

/**
 * 重置用户密码
 * @param {string} userId
 * @param {string} newPassword
 */
export function resetUserPassword(userId, newPassword) {
  return request({
    url: `/api/v1/admin/users/${userId}/password`,
    method: 'post',
    data: { new_password: newPassword }
  });
}

/**
 * 获取用户学习数据
 * @param {string} userId
 * @param {number} timeWindowDays
 */
export function getUserLearningData(userId, timeWindowDays = 30) {
  return request({
    url: `/api/v1/admin/users/${userId}/learning-data`,
    method: 'get',
    params: { time_window_days: timeWindowDays }
  });
}

/**
 * 更新用户信息 (保留接口，虽然文档片段未明确列出通用更新，但通常存在)
 * @param {string} userId
 * @param {Object} data
 */
export function updateUser(userId, data) {
  return request({
    url: `/api/v1/admin/users/${userId}`,
    method: 'put',
    data
  });
}

/**
 * 设置用户角色 (保留接口)
 * @param {string} userId
 * @param {string} role 'student' | 'admin'
 */
export function updateUserRole(userId, role) {
  return request({
    url: `/api/v1/admin/users/${userId}/role`,
    method: 'put',
    data: { role }
  });
}
