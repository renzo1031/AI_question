import request from '../utils/request';

/**
 * 获取知识点列表
 * @param {Object} params { page, page_size, grade_id, subject_id, keyword, with_subject, with_grade }
 */
export function getKnowledgePointList(params) {
  return request({
    url: '/api/v1/admin/grade-knowledge/knowledge-points',
    method: 'get',
    params
  });
}

/**
 * 获取知识点详情
 * @param {number} kpId
 * @param {Object} params { with_subject, with_grade }
 */
export function getKnowledgePointDetail(kpId, params) {
  return request({
    url: `/api/v1/admin/grade-knowledge/knowledge-points/${kpId}`,
    method: 'get',
    params
  });
}

/**
 * 创建知识点
 * @param {Object} data { name, grade_id, subject_id, description, sort_order }
 */
export function createKnowledgePoint(data) {
  return request({
    url: '/api/v1/admin/grade-knowledge/knowledge-points',
    method: 'post',
    data
  });
}

/**
 * 更新知识点
 * @param {number} kpId
 * @param {Object} data { name, description, sort_order }
 */
export function updateKnowledgePoint(kpId, data) {
  return request({
    url: `/api/v1/admin/grade-knowledge/knowledge-points/${kpId}`,
    method: 'put',
    data
  });
}

/**
 * 删除知识点
 * @param {number} kpId
 */
export function deleteKnowledgePoint(kpId) {
  return request({
    url: `/api/v1/admin/grade-knowledge/knowledge-points/${kpId}`,
    method: 'delete'
  });
}
