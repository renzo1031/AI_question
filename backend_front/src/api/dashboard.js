import request from '../utils/request';

/**
 * 获取看板概览数据 (用户统计、题目统计、练习统计)
 * @param {string} period 统计周期，'7d', '15d', '30d'
 */
export function getDashboardData(period = '7d') {
  return request({
    url: '/api/v1/admin/dashboard/overview',
    method: 'get',
    params: { period }
  });
}

/**
 * 获取系统整体统计数据 (兼容旧接口，如有需要请确认是否保留)
 */
export function getStatistics() {
  return request({
    url: '/api/v1/admin/statistics',
    method: 'get'
  });
}

/**
 * 获取每日统计趋势 (兼容旧接口，如有需要请确认是否保留)
 * @param {number} days 天数
 */
export function getDailyStatistics(days = 7) {
  return request({
    url: '/api/v1/admin/statistics/daily',
    method: 'get',
    params: { days }
  });
}
