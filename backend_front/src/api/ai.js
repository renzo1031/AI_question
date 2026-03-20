import request from '../utils/request';

/**
 * 获取当前 LLM 配置（兼容旧接口，推荐使用 config.js 中的 getLlmConfig）
 * @deprecated 请使用 config.js 中的 getLlmConfig
 */
export function getAiConfig() {
  return request({
    url: '/api/v1/admin/configs/llm',
    method: 'get'
  });
}

/**
 * 更新 LLM 配置（兼容旧接口，推荐使用 config.js 中的 updateLlmConfig）
 * @param {Object} data
 * @deprecated 请使用 config.js 中的 updateLlmConfig
 */
export function updateAiConfig(data) {
  return request({
    url: '/api/v1/admin/configs/llm',
    method: 'put',
    data
  });
}
