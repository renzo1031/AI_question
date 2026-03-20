<template>
  <div class="announcement-list-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="关键词">
          <a-input v-model:value="searchParams.keyword" placeholder="公告标题/内容" allow-clear />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchParams.is_active" placeholder="全部" style="width: 120px" allow-clear>
            <a-select-option :value="true">启用</a-select-option>
            <a-select-option :value="false">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="公告列表" :bordered="false" style="margin-top: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">新增公告</a-button>
      </template>
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'is_active'">
            <a-switch
              :checked="record.is_active"
              :loading="record.statusLoading"
              @change="(checked) => handleStatusChange(record, checked)"
            />
          </template>

          <template v-else-if="column.dataIndex === 'start_at'">
            {{ formatDate(record.start_at) }}
          </template>

          <template v-else-if="column.dataIndex === 'end_at'">
            {{ formatDate(record.end_at) }}
          </template>

          <template v-else-if="column.dataIndex === 'action'">
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个公告吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="handleDelete(record)"
            >
              <a style="color: red">删除</a>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      :confirmLoading="modalLoading"
      width="600px"
    >
      <a-form :model="formData" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }" ref="formRef">
        <a-form-item label="标题" name="title" :rules="[{ required: true, message: '请输入公告标题' }]">
          <a-input v-model:value="formData.title" />
        </a-form-item>
        <a-form-item label="内容" name="content" :rules="[{ required: true, message: '请输入公告内容' }]">
          <a-textarea v-model:value="formData.content" :rows="4" />
        </a-form-item>
        <a-form-item label="生效时间" name="start_at">
          <a-date-picker show-time v-model:value="formData.start_at" valueFormat="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </a-form-item>
        <a-form-item label="失效时间" name="end_at">
          <a-date-picker show-time v-model:value="formData.end_at" valueFormat="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </a-form-item>
        <a-form-item label="排序" name="sort_order">
          <a-input-number v-model:value="formData.sort_order" style="width: 100%" :min="0" />
        </a-form-item>
        <a-form-item label="状态" name="is_active">
          <a-switch v-model:checked="formData.is_active" />
          <span style="margin-left: 8px">{{ formData.is_active ? '启用' : '禁用' }}</span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { getAnnouncementList, createAnnouncement, updateAnnouncement, deleteAnnouncement, updateAnnouncementStatus } from '../api/announcement';

const loading = ref(false);
const dataSource = ref([]);

const searchParams = reactive({
  keyword: '',
  is_active: undefined
});

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
});

const columns = [
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    width: 200,
  },
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 100,
  },
  {
    title: '生效时间',
    dataIndex: 'start_at',
    key: 'start_at',
    width: 180,
  },
  {
    title: '失效时间',
    dataIndex: 'end_at',
    key: 'end_at',
    width: 180,
  },
  {
    title: '排序',
    dataIndex: 'sort_order',
    key: 'sort_order',
    width: 80,
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 150,
  },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchParams
    };
    
    // Clean undefined params
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') delete params[key];
    });

    const res = await getAnnouncementList(params);
    dataSource.value = (res.data || []).map(item => ({ ...item, statusLoading: false }));
    if (res.page_info) {
      pagination.total = res.page_info.total;
    } else {
      pagination.total = res.total || 0;
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchData();
};

const handleSearch = () => {
  pagination.current = 1;
  fetchData();
};

const handleReset = () => {
  searchParams.keyword = '';
  searchParams.is_active = undefined;
  handleSearch();
};

const handleStatusChange = async (record, checked) => {
  record.statusLoading = true;
  try {
    await updateAnnouncementStatus(record.id, checked);
    record.is_active = checked;
    message.success('状态更新成功');
  } catch (error) {
    console.error(error);
    message.error('状态更新失败');
    // Revert switch state if failed (though visually it might be tricky without full reload, 
    // but here we just keep it as is or reload)
    fetchData(); 
  } finally {
    record.statusLoading = false;
  }
};

// Modal
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalTitle = ref('新增公告');
const formRef = ref(null);
const formData = reactive({
  id: undefined,
  title: '',
  content: '',
  start_at: null,
  end_at: null,
  sort_order: 0,
  is_active: false
});

const handleAdd = () => {
  modalTitle.value = '新增公告';
  Object.assign(formData, {
    id: undefined,
    title: '',
    content: '',
    start_at: null,
    end_at: null,
    sort_order: 0,
    is_active: true
  });
  modalVisible.value = true;
};

const handleEdit = (record) => {
  modalTitle.value = '编辑公告';
  Object.assign(formData, {
    id: record.id,
    title: record.title,
    content: record.content,
    start_at: record.start_at,
    end_at: record.end_at,
    sort_order: record.sort_order,
    is_active: record.is_active
  });
  modalVisible.value = true;
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    modalLoading.value = true;
    
    const data = { ...formData };
    delete data.id; // Don't send ID in body

    if (formData.id) {
      await updateAnnouncement(formData.id, data);
      message.success('更新成功');
    } else {
      await createAnnouncement(data);
      message.success('创建成功');
    }
    modalVisible.value = false;
    fetchData();
  } catch (error) {
    console.error(error);
  } finally {
    modalLoading.value = false;
  }
};

const handleDelete = async (record) => {
  try {
    await deleteAnnouncement(record.id);
    message.success('删除成功');
    fetchData();
  } catch (error) {
    console.error(error);
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.announcement-list-container {
  min-height: 100%;
}
</style>
