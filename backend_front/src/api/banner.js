import request from '../utils/request';

/**
 * 上传轮播图图片
 * @param {File} file
 */
export function uploadBannerImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request({
    url: '/api/v1/admin/banners/upload-image',
    method: 'post',
    data: formData
  });
}

/**
 * 获取轮播图列表
 * @param {Object} params { page, page_size, keyword, is_active }
 */
export function getBannerList(params) {
  return request({
    url: '/api/v1/admin/banners',
    method: 'get',
    params
  });
}

/**
 * 创建轮播图
 * @param {Object} data { title, image_url, image_key, link_url, link_type, is_active, start_at, end_at, sort_order }
 */
export function createBanner(data) {
  return request({
    url: '/api/v1/admin/banners',
    method: 'post',
    data
  });
}

/**
 * 获取轮播图详情
 * @param {number} bannerId
 */
export function getBannerDetail(bannerId) {
  return request({
    url: `/api/v1/admin/banners/${bannerId}`,
    method: 'get'
  });
}

/**
 * 更新轮播图
 * @param {number} bannerId
 * @param {Object} data { image_url, image_key, link_url, link_type, is_active, start_at, end_at, sort_order }
 */
export function updateBanner(bannerId, data) {
  return request({
    url: `/api/v1/admin/banners/${bannerId}`,
    method: 'put',
    data
  });
}

/**
 * 删除轮播图
 * @param {number} bannerId
 */
export function deleteBanner(bannerId) {
  return request({
    url: `/api/v1/admin/banners/${bannerId}`,
    method: 'delete'
  });
}

/**
 * 启用/停用轮播图
 * @param {number} bannerId
 * @param {boolean} isActive
 */
export function setBannerActive(bannerId, isActive) {
  return request({
    url: `/api/v1/admin/banners/${bannerId}/active`,
    method: 'patch',
    params: { is_active: isActive }
  });
}
