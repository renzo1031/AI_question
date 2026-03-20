import request from '../utils/request';

/**
 * 获取学科列表
 * @param {Object} params { page, page_size, grade_id, keyword, with_grade, with_knowledge_points }
 */
export function getSubjectList(params) {
  return request({
    url: '/api/v1/admin/grade-knowledge/subjects',
    method: 'get',
    params
  });
}

/**
 * 获取学科详情
 * @param {number} subjectId
 * @param {Object} params { with_grade, with_knowledge_points }
 */
export function getSubjectDetail(subjectId, params) {
  return request({
    url: `/api/v1/admin/grade-knowledge/subjects/${subjectId}`,
    method: 'get',
    params
  });
}

/**
 * 创建学科
 * @param {Object} data { name, grade_id, description, sort_order }
 */
export function createSubject(data) {
  return request({
    url: '/api/v1/admin/grade-knowledge/subjects',
    method: 'post',
    data
  });
}

/**
 * 更新学科
 * @param {number} subjectId
 * @param {Object} data { name, description, sort_order }
 */
export function updateSubject(subjectId, data) {
  return request({
    url: `/api/v1/admin/grade-knowledge/subjects/${subjectId}`,
    method: 'put',
    data
  });
}

/**
 * 删除学科
 * @param {number} subjectId
 */
export function deleteSubject(subjectId) {
  return request({
    url: `/api/v1/admin/grade-knowledge/subjects/${subjectId}`,
    method: 'delete'
  });
}

/**
 * 获取指定学科的知识点列表
 * @param {number} subjectId
 * @param {Object} params { page, page_size, keyword }
 */
export function getKnowledgePointsBySubject(subjectId, params) {
  return request({
    url: `/api/v1/admin/grade-knowledge/subjects/${subjectId}/knowledge-points`,
    method: 'get',
    params
  });
}
