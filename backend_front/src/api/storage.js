import request from '../utils/request';

/**
 * 获取支持的存储服务商列表
 */
export function getStorageProviders() {
  return request({
    url: '/api/v1/admin/storage/providers',
    method: 'get'
  });
}

/**
 * 获取存储配置
 */
export function getStorageConfig() {
  return request({
    url: '/api/v1/admin/storage/config',
    method: 'get'
  });
}

/**
 * 更新存储配置 (根据惯例推断)
 * @param {Object} data
 */
export function updateStorageConfig(data) {
  return request({
    url: '/api/v1/admin/storage/config',
    method: 'put', // Assuming PUT for update
    data
  });
}
