import request from '../utils/request';

/**
 * 获取年级列表 (分页)
 * @param {Object} params { page, page_size, keyword, with_subjects, with_knowledge_points }
 */
export function getGradeList(params) {
  return request({
    url: '/api/v1/admin/grade-knowledge/grades',
    method: 'get',
    params
  });
}

/**
 * 获取所有年级 (不分页)
 * @param {Object} params { with_subjects, with_knowledge_points }
 */
export function getAllGrades(params) {
  return request({
    url: '/api/v1/admin/grade-knowledge/grades/all',
    method: 'get',
    params
  });
}

/**
 * 获取年级详情
 * @param {number} gradeId
 * @param {Object} params { with_subjects, with_knowledge_points }
 */
export function getGradeDetail(gradeId, params) {
  return request({
    url: `/api/v1/admin/grade-knowledge/grades/${gradeId}`,
    method: 'get',
    params
  });
}

/**
 * 创建年级
 * @param {Object} data { name, description, sort_order }
 */
export function createGrade(data) {
  return request({
    url: '/api/v1/admin/grade-knowledge/grades',
    method: 'post',
    data
  });
}

/**
 * 更新年级
 * @param {number} gradeId
 * @param {Object} data { name, description, sort_order }
 */
export function updateGrade(gradeId, data) {
  return request({
    url: `/api/v1/admin/grade-knowledge/grades/${gradeId}`,
    method: 'put',
    data
  });
}

/**
 * 删除年级
 * @param {number} gradeId
 */
export function deleteGrade(gradeId) {
  return request({
    url: `/api/v1/admin/grade-knowledge/grades/${gradeId}`,
    method: 'delete'
  });
}

/**
 * 获取指定年级的学科列表
 * @param {number} gradeId
 * @param {Object} params { page, page_size, keyword, with_knowledge_points }
 */
export function getSubjectsByGrade(gradeId, params) {
  return request({
    url: `/api/v1/admin/grade-knowledge/grades/${gradeId}/subjects`,
    method: 'get',
    params
  });
}
