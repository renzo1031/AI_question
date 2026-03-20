import request from '../utils/request';

// ================= 邮件配置 =================

/**
 * 获取邮件配置
 */
export function getEmailConfig() {
  return request({
    url: '/api/v1/admin/system-config/email',
    method: 'get'
  });
}

/**
 * 更新邮件配置
 * @param {Object} data { smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, is_enabled }
 */
export function updateEmailConfig(data) {
  return request({
    url: '/api/v1/admin/system-config/email',
    method: 'post',
    data
  });
}

/**
 * 测试邮件配置
 * @param {Object} data { to_email, subject, content }
 */
export function testEmailConfig(data) {
  return request({
    url: '/api/v1/admin/system-config/email/test',
    method: 'post',
    data
  });
}

// ================= 短信配置 =================

/**
 * 获取短信配置
 */
export function getSmsConfig() {
  return request({
    url: '/api/v1/admin/system-config/sms',
    method: 'get'
  });
}

/**
 * 更新短信配置
 * @param {Object} data 配置对象
 */
export function updateSmsConfig(data) {
  return request({
    url: '/api/v1/admin/system-config/sms',
    method: 'post',
    data
  });
}

/**
 * 测试短信配置
 * @param {Object} data { phone, code }
 */
export function testSmsConfig(data) {
  return request({
    url: '/api/v1/admin/system-config/sms/test',
    method: 'post',
    data
  });
}
