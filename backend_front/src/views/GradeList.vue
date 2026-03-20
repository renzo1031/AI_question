<template>
  <div class="grade-list-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="关键词">
          <a-input v-model:value="searchParams.keyword" placeholder="年级名称" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="年级列表" :bordered="false" style="margin-top: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">新增年级</a-button>
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
          <template v-if="column.dataIndex === 'action'">
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个年级吗？删除将级联删除其下所有知识点！"
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
    >
      <a-form :model="formData" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }" ref="formRef">
        <a-form-item label="年级名称" name="name" :rules="[{ required: true, message: '请输入年级名称' }]">
          <a-input v-model:value="formData.name" placeholder="如：一年级" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="formData.description" placeholder="年级描述" />
        </a-form-item>
        <a-form-item label="排序" name="sort_order">
          <a-input-number v-model:value="formData.sort_order" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { getGradeList, createGrade, updateGrade, deleteGrade } from '../api/grade';

const loading = ref(false);
const dataSource = ref([]);
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
});

const searchParams = reactive({
  keyword: ''
});

const columns = [
  { title: '年级名称', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description' },
  { title: '操作', dataIndex: 'action', width: 150 }
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchParams.keyword
    };
    const res = await getGradeList(params);
    let list = res.data || [];
    
    // Client-side sort by sort_order ascending
    list.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
    
    dataSource.value = list;
    if (res.page_info) {
        pagination.total = res.page_info.total;
    } else {
        // Fallback if structure is different
        pagination.total = res.total || 0;
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
  searchParams.keyword = '';
  handleSearch();
};

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchData();
};

// Modal Logic
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalTitle = ref('新增年级');
const formRef = ref(null);
const formData = reactive({
  id: undefined,
  name: '',
  description: '',
  sort_order: 0
});

const handleAdd = () => {
  modalTitle.value = '新增年级';
  formData.id = undefined;
  formData.name = '';
  formData.description = '';
  formData.sort_order = pagination.total + 1;
  modalVisible.value = true;
};

const handleEdit = (record) => {
  modalTitle.value = '编辑年级';
  formData.id = record.id;
  formData.name = record.name;
  formData.description = record.description;
  formData.sort_order = record.sort_order;
  modalVisible.value = true;
};

const handleDelete = async (record) => {
  try {
    await deleteGrade(record.id);
    message.success('删除成功');
    fetchData();
  } catch (error) {
    console.error(error);
  }
};

const handleModalOk = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
    modalLoading.value = true;
    
    if (formData.id) {
      await updateGrade(formData.id, {
        name: formData.name,
        description: formData.description,
        sort_order: formData.sort_order
      });
      message.success('更新成功');
    } else {
      await createGrade({
        name: formData.name,
        description: formData.description,
        sort_order: formData.sort_order
      });
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

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.grade-list-container {
  padding: 24px;
}
</style>
