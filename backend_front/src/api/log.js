import request from '../utils/request';

/**
 * 获取系统日志列表
 * @param {Object} params { page, page_size, user_type, user_id, username, log_level, module, action, is_success, start_time, end_time }
 */
export function getSystemLogs(params) {
  return request({
    url: '/api/v1/admin/operation-logs',
    method: 'get',
    params
  });
}

/**
 * 获取日志详情
 * @param {String} id
 */
export function getLogDetail(id) {
  return request({
    url: `/api/v1/admin/operation-logs/${id}`,
    method: 'get'
  });
}

/**
 * 获取日志统计信息
 * @param {Object} params { start_time, end_time, user_type }
 */
export function getLogStatistics(params) {
  return request({
    url: '/api/v1/admin/operation-logs/stats/summary',
    method: 'get',
    params
  });
}

/**
 * 清理旧日志
 * @param {Number} days 保留天数
 */
export function cleanLogs(days) {
  return request({
    url: '/api/v1/admin/operation-logs/cleanup',
    method: 'delete',
    params: { days }
  });
}
