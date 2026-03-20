import request from '../utils/request';

// --- 题目管理 ---

/**
 * 获取题目列表
 * @param {Object} params { page, page_size, question_id, question_type, subject, difficulty, source, tag_id, keyword }
 */
export function getQuestionList(params) {
  return request({
    url: '/api/v1/admin/question-bank/questions',
    method: 'get',
    params
  });
}

/**
 * 获取题目详情
 * @param {string} questionId
 */
export function getQuestionDetail(questionId) {
  return request({
    url: `/api/v1/admin/question-bank/questions/${questionId}`,
    method: 'get'
  });
}

/**
 * 创建题目
 * @param {Object} data
 */
export function createQuestion(data) {
  return request({
    url: '/api/v1/admin/question-bank/questions',
    method: 'post',
    data
  });
}

/**
 * 更新题目
 * @param {string} questionId
 * @param {Object} data
 */
export function updateQuestion(questionId, data) {
  return request({
    url: `/api/v1/admin/question-bank/questions/${questionId}`,
    method: 'put',
    data
  });
}

/**
 * 删除题目
 * @param {string} questionId
 */
export function deleteQuestion(questionId) {
  return request({
    url: `/api/v1/admin/question-bank/questions/${questionId}`,
    method: 'delete'
  });
}

/**
 * 批量导入题目
 * @param {Object} data { items: [] }
 */
export function importQuestions(data) {
  return request({
    url: '/api/v1/admin/question-bank/questions/import',
    method: 'post',
    data
  });
}

/**
 * 导出题目
 * @param {Object} params 同列表查询参数
 */
export function exportQuestions(params) {
  return request({
    url: '/api/v1/admin/question-bank/questions/export',
    method: 'get',
    params
  });
}

// --- 标签管理 ---

/**
 * 获取标签列表
 * @param {Object} params { page, page_size, keyword }
 */
export function getTagList(params) {
  return request({
    url: '/api/v1/admin/question-bank/tags',
    method: 'get',
    params
  });
}

/**
 * 获取标签详情
 * @param {string} tagId
 */
export function getTagDetail(tagId) {
  return request({
    url: `/api/v1/admin/question-bank/tags/${tagId}`,
    method: 'get'
  });
}

/**
 * 创建标签
 * @param {Object} data { name, description, parent_id, level }
 */
export function createTag(data) {
  return request({
    url: '/api/v1/admin/question-bank/tags',
    method: 'post',
    data
  });
}

/**
 * 更新标签
 * @param {string} tagId
 * @param {Object} data
 */
export function updateTag(tagId, data) {
  return request({
    url: `/api/v1/admin/question-bank/tags/${tagId}`,
    method: 'put',
    data
  });
}

/**
 * 删除标签
 * @param {string} tagId
 */
export function deleteTag(tagId) {
  return request({
    url: `/api/v1/admin/question-bank/tags/${tagId}`,
    method: 'delete'
  });
}
