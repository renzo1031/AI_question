<template>
  <div class="banner-list-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="状态">
          <a-select v-model:value="searchParams.is_active" placeholder="全部" style="width: 120px" allow-clear>
            <a-select-option :value="true">启用</a-select-option>
            <a-select-option :value="false">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
          <a-button type="primary" style="margin-left: 24px" @click="showCreateModal">新建轮播图</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="轮播图列表" :bordered="false" style="margin-top: 24px">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="pagination"
        :loading="loading"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'image_url'">
            <a-image :width="200" :src="formatImageUrl(record.image_url)" />
          </template>
          
          <template v-else-if="column.dataIndex === 'is_active'">
            <a-tag :color="record.is_active ? 'success' : 'error'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          
          <template v-else-if="column.dataIndex === 'start_at'">
            {{ record.start_at ? new Date(record.start_at).toLocaleString() : '-' }}
          </template>

          <template v-else-if="column.dataIndex === 'end_at'">
            {{ record.end_at ? new Date(record.end_at).toLocaleString() : '-' }}
          </template>
          
          <template v-else-if="column.dataIndex === 'action'">
            <a @click="showDetailModal(record)">详情</a>
            <a-divider type="vertical" />
            <a @click="showEditModal(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm 
              v-if="record.is_active"
              title="确定禁用该轮播图吗？" 
              @confirm="handleStatusChange(record, false)"
            >
              <a style="color: #faad14">禁用</a>
            </a-popconfirm>
            <a-popconfirm 
              v-else
              title="确定启用该轮播图吗？" 
              @confirm="handleStatusChange(record, true)"
            >
              <a style="color: #52c41a">启用</a>
            </a-popconfirm>
            <a-divider type="vertical" />
            <a-popconfirm 
              title="确定删除该轮播图吗？此操作不可恢复！" 
              @confirm="handleDelete(record)"
            >
              <a style="color: #ff4d4f">删除</a>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Detail Modal -->
    <a-modal
      v-model:open="detailVisible"
      title="轮播图详情"
      :footer="null"
      width="800px"
    >
      <a-spin :spinning="detailLoading">
        <div style="display: flex; justify-content: center; margin-bottom: 24px;">
          <a-image :width="400" :src="formatImageUrl(currentDetail.image_url)" />
        </div>

        <a-descriptions bordered :column="2">
          <a-descriptions-item label="ID">{{ currentDetail.id }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="currentDetail.is_active ? 'success' : 'error'">
              {{ currentDetail.is_active ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="排序值">{{ currentDetail.sort_order }}</a-descriptions-item>
          <a-descriptions-item label="链接类型">
            <span v-if="currentDetail.link_type === 'internal'">内部链接</span>
            <span v-else-if="currentDetail.link_type === 'external'">外部链接</span>
            <span v-else>无跳转</span>
          </a-descriptions-item>
          <a-descriptions-item label="跳转链接">{{ currentDetail.link_url || '-' }}</a-descriptions-item>
          <a-descriptions-item label="生效时间">{{ currentDetail.start_at ? new Date(currentDetail.start_at).toLocaleString() : '-' }}</a-descriptions-item>
          <a-descriptions-item label="失效时间">{{ currentDetail.end_at ? new Date(currentDetail.end_at).toLocaleString() : '-' }}</a-descriptions-item>
          <a-descriptions-item label="创建人ID">{{ currentDetail.created_by_admin_id || '-' }}</a-descriptions-item>
          <a-descriptions-item label="更新人ID">{{ currentDetail.updated_by_admin_id || '-' }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ currentDetail.created_at ? new Date(currentDetail.created_at).toLocaleString() : '-' }}</a-descriptions-item>
          <a-descriptions-item label="更新时间">{{ currentDetail.updated_at ? new Date(currentDetail.updated_at).toLocaleString() : '-' }}</a-descriptions-item>
        </a-descriptions>
        
        <div style="text-align: center; margin-top: 24px;">
          <a-button type="primary" @click="handleDetailEdit">编辑</a-button>
          <a-button style="margin-left: 8px" @click="detailVisible = false">关闭</a-button>
        </div>
      </a-spin>
    </a-modal>

    <!-- Image Crop Modal -->
    <image-cropper
      v-model:visible="cropVisible"
      :image-src="cropImageSrc"
      @confirm="handleCropConfirm"
    />

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑轮播图' : '新建轮播图'"
      @ok="handleModalOk"
      :confirmLoading="actionLoading"
      width="600px"
    >
      <a-form :model="formState" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="轮播图片" name="image_url" required>
          <a-upload
            list-type="picture-card"
            :show-upload-list="false"
            :before-upload="beforeUpload"
          >
            <img v-if="previewImage || formState.image_url" :src="previewImage || formatImageUrl(formState.image_url)" alt="banner" style="width: 100%" />
            <div v-else>
              <plus-outlined />
              <div style="margin-top: 8px">上传</div>
            </div>
          </a-upload>
          <div style="color: #999; font-size: 12px; margin-top: 8px;">建议尺寸：1920x400，支持 jpg, png, jpeg</div>
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="跳转链接" name="link_url">
              <a-input v-model:value="formState.link_url" placeholder="请输入跳转链接" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="链接类型" name="link_type">
              <a-select v-model:value="formState.link_type">
                <a-select-option value="none">无跳转</a-select-option>
                <a-select-option value="internal">内部链接</a-select-option>
                <a-select-option value="external">外部链接</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序值" name="sort_order">
              <a-input-number v-model:value="formState.sort_order" style="width: 100%" :min="0" placeholder="值越大越靠前" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态" name="is_active">
              <a-switch v-model:checked="formState.is_active" checked-children="启用" un-checked-children="禁用" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="生效时间" name="start_at">
              <a-date-picker show-time v-model:value="formState.start_at" style="width: 100%" value-format="YYYY-MM-DD HH:mm:ss" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="失效时间" name="end_at">
              <a-date-picker show-time v-model:value="formState.end_at" style="width: 100%" value-format="YYYY-MM-DD HH:mm:ss" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { PlusOutlined } from '@ant-design/icons-vue';
import ImageCropper from '../components/ImageCropper.vue';
import { 
  getBannerList, 
  createBanner, 
  updateBanner, 
  deleteBanner, 
  setBannerActive,
  uploadBannerImage,
  getBannerDetail
} from '../api/banner';

const loading = ref(false);
const actionLoading = ref(false);
const dataSource = ref([]);
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
});

const searchParams = reactive({
  is_active: undefined,
});

const columns = [
  {
    title: '图片',
    dataIndex: 'image_url',
    width: 250,
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    width: 100,
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: 250,
    fixed: 'right',
  },
];

// Detail Modal
const detailVisible = ref(false);
const detailLoading = ref(false);
const currentDetail = ref({});

const showDetailModal = async (record) => {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    const res = await getBannerDetail(record.id);
    if (res.code === 0) {
      currentDetail.value = res.data;
    } else {
      message.error(res.message || '获取详情失败');
    }
  } catch (error) {
    console.error(error);
    message.error('获取详情出错');
  } finally {
    detailLoading.value = false;
  }
};

const handleDetailEdit = () => {
  detailVisible.value = false;
  showEditModal(currentDetail.value);
};

// Modal & Form
const modalVisible = ref(false);
const isEdit = ref(false);
const formRef = ref();
const currentId = ref(null);
const fileList = ref([]);
const previewImage = ref('');

const formState = reactive({
  image_url: '',
  image_key: '',
  link_url: '',
  link_type: 'none',
  is_active: true,
  sort_order: 0,
  start_at: null,
  end_at: null,
});

const validateImage = async (_rule, value) => {
  if (fileList.value.length > 0) {
    return Promise.resolve();
  }
  if (formState.image_url) {
    return Promise.resolve();
  }
  return Promise.reject('请上传图片');
};

const rules = {
  image_url: [{ required: true, validator: validateImage, trigger: 'change' }],
};

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchParams,
    };
    
    // 清理 undefined 值
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    const res = await getBannerList(params);
    if (res.code === 0) {
      // 适配新的返回结构
      if (Array.isArray(res.data)) {
        dataSource.value = res.data;
        pagination.total = res.page_info?.total || res.data.length;
      } else {
        // 兼容旧结构
        dataSource.value = res.data.items || [];
        pagination.total = res.data.total || 0;
      }
    } else {
      message.error(res.message || '获取列表失败');
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.current = 1;
  fetchData();
};

const handleReset = () => {
  searchParams.is_active = undefined;
  handleSearch();
};

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchData();
};

const handleStatusChange = async (record, isActive) => {
  try {
    const res = await setBannerActive(record.id, isActive);
    if (res.code === 0) {
      message.success('操作成功');
      fetchData();
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (error) {
    console.error(error);
  }
};

const handleDelete = async (record) => {
  try {
    const res = await deleteBanner(record.id);
    if (res.code === 0) {
      message.success('删除成功');
      fetchData();
    } else {
      message.error(res.message || '删除失败');
    }
  } catch (error) {
    console.error(error);
  }
};

// Image Crop
const cropVisible = ref(false);
const cropImageSrc = ref('');

const beforeUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 文件!');
    return false;
  }
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    message.error('图片必须小于 10MB!');
    return false;
  }

  // 读取图片并打开裁剪弹窗
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = (e) => {
    cropImageSrc.value = e.target.result;
    cropVisible.value = true;
  };

  return false;
};

const handleCropConfirm = (blob) => {
  const croppedFile = new File([blob], 'banner.jpg', { type: 'image/jpeg' });
  fileList.value = [croppedFile];
  previewImage.value = URL.createObjectURL(blob);
  formRef.value?.validateFields('image_url');
};

const formatImageUrl = (url) => {
  if (!url) return '';
  url = url.trim();
  // 如果是本地 MinIO 地址，通过代理访问以避免 CORS 问题
  if (url.includes('localhost:9000') || url.includes('127.0.0.1:9000')) {
    return url.replace(/^https?:\/\/[^/]+/, '');
  }
  return url;
};

// Modal Actions
const showCreateModal = () => {
  isEdit.value = false;
  currentId.value = null;
  fileList.value = [];
  previewImage.value = '';
  
  // Reset form
  formState.image_url = '';
  formState.image_key = '';
  formState.link_url = '';
  formState.link_type = 'none';
  formState.is_active = true;
  formState.sort_order = 0;
  formState.start_at = null;
  formState.end_at = null;
  
  modalVisible.value = true;
};

const showEditModal = (record) => {
  isEdit.value = true;
  currentId.value = record.id;
  fileList.value = [];
  previewImage.value = '';
  
  // Fill form
  formState.image_url = record.image_url;
  formState.image_key = record.image_key;
  formState.link_url = record.link_url || '';
  formState.link_type = record.link_type || 'none';
  formState.is_active = record.is_active;
  formState.sort_order = record.sort_order || 0;
  formState.start_at = record.start_at;
  formState.end_at = record.end_at;
  
  modalVisible.value = true;
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    actionLoading.value = true;
    
    // 如果有新文件，先上传
    if (fileList.value.length > 0) {
      const file = fileList.value[0];
      try {
        const uploadRes = await uploadBannerImage(file);
        if (uploadRes.code === 0) {
           formState.image_url = uploadRes.data.image_url;
           formState.image_key = uploadRes.data.image_key;
        } else {
           message.error(uploadRes.message || '图片上传失败');
           actionLoading.value = false;
           return;
        }
      } catch (err) {
         console.error(err);
         message.error('图片上传出错');
         actionLoading.value = false;
         return;
      }
    }
    
    const data = { ...formState };
    
    // 处理空值
    if (!data.link_url) data.link_url = null;
    
    // 格式化日期为 ISO 8601
    if (data.start_at) {
      data.start_at = new Date(data.start_at).toISOString();
    } else {
      data.start_at = null;
    }

    if (data.end_at) {
      data.end_at = new Date(data.end_at).toISOString();
    } else {
      data.end_at = null;
    }
    
    let res;
    if (isEdit.value) {
      res = await updateBanner(currentId.value, data);
    } else {
      res = await createBanner(data);
    }
    
    if (res.code === 0) {
      message.success(isEdit.value ? '更新成功' : '创建成功');
      modalVisible.value = false;
      fetchData();
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (error) {
    console.error(error);
  } finally {
    actionLoading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.banner-list-container {
  padding: 24px;
}
</style>
