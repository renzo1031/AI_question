import request from '../utils/request';

/**
 * 获取系统配置列表
 */
export function getConfigList() {
  return request({
    url: '/api/v1/admin/configs',
    method: 'get'
  });
}

/**
 * 创建系统配置
 * @param {Object} data { key, value, description, is_public }
 */
export function createConfig(data) {
  return request({
    url: '/api/v1/admin/configs',
    method: 'post',
    data
  });
}

/**
 * 更新系统配置
 * @param {string} key 配置键
 * @param {Object} data { value, description, is_public }
 */
export function updateConfig(key, data) {
  return request({
    url: `/api/v1/admin/configs/${key}`,
    method: 'put',
    data
  });
}

/**
 * 删除系统配置
 * @param {string} key 配置键
 */
export function deleteConfig(key) {
  return request({
    url: `/api/v1/admin/configs/${key}`,
    method: 'delete'
  });
}

/**
 * 获取OCR配置
 */
export function getOcrConfig() {
  return request({
    url: '/api/v1/admin/configs/ocr',
    method: 'get'
  });
}

/**
 * 更新OCR配置
 * @param {Object} data { provider, app_id, api_key, secret_key, endpoint, is_enabled }
 */
export function updateOcrConfig(data) {
  return request({
    url: '/api/v1/admin/configs/ocr',
    method: 'put',
    data
  });
}

/**
 * 获取LLM配置
 */
export function getLlmConfig() {
  return request({
    url: '/api/v1/admin/configs/llm',
    method: 'get'
  });
}

/**
 * 更新LLM配置
 * @param {Object} data { provider, model_name, api_key, base_url, max_tokens, temperature, is_enabled }
 */
export function updateLlmConfig(data) {
  return request({
    url: '/api/v1/admin/configs/llm',
    method: 'put',
    data
  });
}

/**
 * 获取邮箱配置
 */
export function getEmailConfig() {
  return request({
    url: '/api/v1/admin/configs/email',
    method: 'get'
  });
}

/**
 * 更新邮箱配置
 * @param {Object} data { smtp_server, smtp_port, use_tls, username, password, from_email, from_name, is_enabled }
 */
export function updateEmailConfig(data) {
  return request({
    url: '/api/v1/admin/configs/email',
    method: 'put',
    data
  });
}

/**
 * 获取短信配置
 */
export function getSmsConfig() {
  return request({
    url: '/api/v1/admin/configs/sms',
    method: 'get'
  });
}

/**
 * 更新短信配置
 * @param {Object} data { provider, access_key_id, access_key_secret, sign_name, template_code_login, template_code_register, is_enabled }
 */
export function updateSmsConfig(data) {
  return request({
    url: '/api/v1/admin/configs/sms',
    method: 'put',
    data
  });
}

