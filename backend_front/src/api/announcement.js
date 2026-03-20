import request from '../utils/request';

/**
 * 获取公告列表
 * @param {Object} params { page, page_size, keyword, is_active }
 */
export function getAnnouncementList(params) {
  return request({
    url: '/api/v1/admin/announcements',
    method: 'get',
    params
  });
}

/**
 * 创建公告
 * @param {Object} data { title, content, is_active, start_at, end_at, sort_order }
 */
export function createAnnouncement(data) {
  return request({
    url: '/api/v1/admin/announcements',
    method: 'post',
    data
  });
}

/**
 * 获取公告详情
 * @param {number} id
 */
export function getAnnouncementDetail(id) {
  return request({
    url: `/api/v1/admin/announcements/${id}`,
    method: 'get'
  });
}

/**
 * 更新公告
 * @param {number} id
 * @param {Object} data { title, content, is_active, start_at, end_at, sort_order }
 */
export function updateAnnouncement(id, data) {
  return request({
    url: `/api/v1/admin/announcements/${id}`,
    method: 'put',
    data
  });
}

/**
 * 删除公告
 * @param {number} id
 */
export function deleteAnnouncement(id) {
  return request({
    url: `/api/v1/admin/announcements/${id}`,
    method: 'delete'
  });
}

/**
 * 启用/停用公告
 * @param {number} id
 * @param {boolean} isActive
 */
export function updateAnnouncementStatus(id, isActive) {
  return request({
    url: `/api/v1/admin/announcements/${id}/active`,
    method: 'patch',
    params: { is_active: isActive }
  });
}
