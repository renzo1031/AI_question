import request from '../utils/request';

/**
 * 获取纠错记录列表
 * @param {Object} params { page, page_size, status, question_id }
 */
export function getCorrections(params) {
  return request({
    url: '/api/v1/admin/corrections',
    method: 'get',
    params
  });
}

/**
 * 处理纠错记录
 * @param {Number} id
 * @param {Object} data { status, admin_note }
 */
export function handleCorrection(id, data) {
  return request({
    url: `/api/v1/admin/corrections/${id}`,
    method: 'patch',
    data
  });
}

/**
 * 获取纠错统计信息
 */
export function getCorrectionStats() {
  return request({
    url: '/api/v1/admin/corrections/stats',
    method: 'get'
  });
}
