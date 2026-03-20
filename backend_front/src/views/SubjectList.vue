<template>
  <div class="subject-list-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="所属年级">
          <a-select
            v-model:value="searchParams.grade_id"
            placeholder="全部"
            style="width: 200px"
            allow-clear
            :options="gradeOptions"
            :field-names="{ label: 'name', value: 'id' }"
          />
        </a-form-item>
        <a-form-item label="关键词">
          <a-input v-model:value="searchParams.keyword" placeholder="学科名称" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="学科列表" :bordered="false" style="margin-top: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">新增学科</a-button>
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
          <template v-if="column.dataIndex === 'grade'">
            <a-tag :color="getGradeColor(record.grade?.id)" v-if="record.grade">{{ record.grade.name }}</a-tag>
            <span v-else>-</span>
          </template>

          <template v-else-if="column.dataIndex === 'action'">
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handleKnowledgePoints(record)">知识点管理</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个学科吗？"
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
        <a-form-item label="学科名称" name="name" :rules="[{ required: true, message: '请输入学科名称' }]">
          <a-input v-model:value="formData.name" />
        </a-form-item>
        <a-form-item label="所属年级" name="grade_id" :rules="[{ required: true, message: '请选择所属年级' }]">
          <a-select
            v-model:value="formData.grade_id"
            placeholder="请选择年级"
            :options="gradeOptions"
            :field-names="{ label: 'name', value: 'id' }"
          />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="formData.description" />
        </a-form-item>
        <a-form-item label="排序" name="sort_order">
          <a-input-number v-model:value="formData.sort_order" style="width: 100%" :min="0" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { getSubjectList, createSubject, updateSubject, deleteSubject } from '../api/subject';
import { getGradeList, getAllGrades } from '../api/grade';

const loading = ref(false);
const dataSource = ref([]);
const gradeOptions = ref([]);

const getGradeColor = (id) => {
  const colors = [
    'pink', 'red', 'orange', 'green', 'cyan', 'blue', 'purple', 
    'geekblue', 'magenta', 'volcano', 'gold', 'lime'
  ];
  if (!id) return 'blue';
  return colors[id % colors.length];
};

const searchParams = reactive({
  grade_id: undefined,
  keyword: ''
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
    title: '学科名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '所属年级',
    dataIndex: 'grade',
    key: 'grade',
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 250,
  },
];

const fetchGrades = async () => {
  try {
    const res = await getAllGrades(); // Get all grades without pagination
    gradeOptions.value = res.data || [];
  } catch (error) {
    console.error('Failed to fetch grades:', error);
  }
};

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      grade_id: searchParams.grade_id,
      keyword: searchParams.keyword,
      with_grade: true
    };
    const res = await getSubjectList(params);
    let list = res.data || [];
    
    // Client-side sort by sort_order ascending
    list.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));

    dataSource.value = list;
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
  searchParams.grade_id = undefined;
  searchParams.keyword = '';
  handleSearch();
};

// Modal
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalTitle = ref('新增学科');
const formRef = ref(null);
const formData = reactive({
  id: undefined,
  name: '',
  grade_id: undefined,
  description: '',
  sort_order: 0
});

const handleAdd = () => {
  modalTitle.value = '新增学科';
  Object.assign(formData, {
    id: undefined,
    name: '',
    grade_id: undefined,
    description: '',
    sort_order: pagination.total + 1
  });
  modalVisible.value = true;
};

const handleEdit = (record) => {
  modalTitle.value = '编辑学科';
  Object.assign(formData, {
    id: record.id,
    name: record.name,
    grade_id: record.grade_id,
    description: record.description,
    sort_order: record.sort_order
  });
  modalVisible.value = true;
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    modalLoading.value = true;
    if (formData.id) {
      await updateSubject(formData.id, formData);
      message.success('更新成功');
    } else {
      await createSubject(formData);
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
    await deleteSubject(record.id);
    message.success('删除成功');
    fetchData();
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  fetchGrades();
  fetchData();
});
</script>

<style scoped>
.subject-list-container {
  min-height: 100%;
}
</style>
