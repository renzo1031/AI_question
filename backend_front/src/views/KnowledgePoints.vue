<template>
  <div class="kp-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="所属年级">
          <a-select
            v-model:value="searchParams.grade_id"
            placeholder="全部"
            style="width: 150px"
            allow-clear
            :options="gradeOptions"
            :field-names="{ label: 'name', value: 'id' }"
            @change="handleGradeChange"
          />
        </a-form-item>
        <a-form-item label="所属学科">
          <a-select
            v-model:value="searchParams.subject_id"
            placeholder="全部"
            style="width: 150px"
            allow-clear
            :options="subjectOptions"
            :field-names="{ label: 'name', value: 'id' }"
            :disabled="!searchParams.grade_id && !subjectOptions.length"
          />
        </a-form-item>
        <a-form-item label="关键词">
          <a-input v-model:value="searchParams.keyword" placeholder="知识点名称" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="知识点列表" :bordered="false" style="margin-top: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">新增知识点</a-button>
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
            <a-tag :color="getGradeColor(record.subject?.grade?.id)" v-if="record.subject?.grade">{{ record.subject.grade.name }}</a-tag>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.dataIndex === 'subject'">
            <a-tag color="cyan" v-if="record.subject">{{ record.subject.name }}</a-tag>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除这个知识点吗？"
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
        <a-form-item label="名称" name="name" :rules="[{ required: true, message: '请输入名称' }]">
          <a-input v-model:value="formData.name" />
        </a-form-item>
        
        <!-- Grade Selection in Modal -->
        <a-form-item label="所属年级" name="grade_id" :rules="[{ required: true, message: '请选择年级' }]">
             <a-select
            v-model:value="formData.grade_id"
            placeholder="请选择年级"
            :options="gradeOptions"
            :field-names="{ label: 'name', value: 'id' }"
            @change="handleModalGradeChange"
          />
        </a-form-item>

        <a-form-item label="所属学科" name="subject_id" :rules="[{ required: true, message: '请选择学科' }]">
          <a-select
            v-model:value="formData.subject_id"
            placeholder="请选择学科"
            :options="modalSubjectOptions"
            :field-names="{ label: 'name', value: 'id' }"
            :disabled="!formData.grade_id"
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
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { getKnowledgePointList, createKnowledgePoint, updateKnowledgePoint, deleteKnowledgePoint } from '../api/knowledge';
import { getGradeList, getAllGrades, getSubjectsByGrade } from '../api/grade';
import { getSubjectList } from '../api/subject';

const route = useRoute();
const loading = ref(false);
const dataSource = ref([]);
const gradeOptions = ref([]);
const subjectOptions = ref([]); // For search filter
const modalSubjectOptions = ref([]); // For modal

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
  subject_id: undefined,
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
    title: '知识点名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '所属年级',
    dataIndex: 'grade',
    key: 'grade',
  },
  {
    title: '所属学科',
    dataIndex: 'subject',
    key: 'subject',
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
    const res = await getAllGrades();
    gradeOptions.value = res.data || [];
  } catch (error) {
    console.error('Failed to fetch grades:', error);
  }
};

const fetchSubjects = async (gradeId, targetRef) => {
  if (!gradeId) {
    targetRef.value = [];
    return;
  }
  try {
    const res = await getSubjectsByGrade(gradeId, { page: 1, page_size: 200 });
    targetRef.value = res.data || [];
  } catch (error) {
    console.error('Failed to fetch subjects:', error);
  }
};

const handleGradeChange = async (val) => {
  searchParams.subject_id = undefined;
  await fetchSubjects(val, subjectOptions);
};

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      grade_id: searchParams.grade_id,
      subject_id: searchParams.subject_id,
      keyword: searchParams.keyword,
      with_grade: true,
      with_subject: true
    };
    const res = await getKnowledgePointList(params);
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
  searchParams.subject_id = undefined;
  searchParams.keyword = '';
  subjectOptions.value = [];
  handleSearch();
};

// Modal
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalTitle = ref('新增知识点');
const formRef = ref(null);
const formData = reactive({
  id: undefined,
  name: '',
  grade_id: undefined,
  subject_id: undefined,
  description: '',
  sort_order: 0
});

const handleModalGradeChange = async (val) => {
    formData.subject_id = undefined;
    await fetchSubjects(val, modalSubjectOptions);
};

const handleAdd = () => {
  modalTitle.value = '新增知识点';
  Object.assign(formData, {
    id: undefined,
    name: '',
    grade_id: searchParams.grade_id, // Pre-fill if selected in filter
    subject_id: searchParams.subject_id, // Pre-fill if selected in filter
    description: '',
    sort_order: pagination.total + 1
  });
  
  if (formData.grade_id) {
      fetchSubjects(formData.grade_id, modalSubjectOptions);
  } else {
      modalSubjectOptions.value = [];
  }
  
  modalVisible.value = true;
};

const handleEdit = async (record) => {
  modalTitle.value = '编辑知识点';
  
  // We need to fetch subjects for the grade of this record
  const gradeId = record.grade ? record.grade.id : record.grade_id; // Try to get from object or direct field
  
  // Note: record might not have grade_id directly if it's nested in grade object, 
  // but usually API returns flat object or we need to extract.
  // Assuming record has grade_id or we extract from record.grade.id
  
  const actualGradeId = gradeId || (record.subject ? record.subject.grade_id : undefined);

  if (actualGradeId) {
      await fetchSubjects(actualGradeId, modalSubjectOptions);
  }

  Object.assign(formData, {
    id: record.id,
    name: record.name,
    grade_id: actualGradeId,
    subject_id: record.subject_id,
    description: record.description,
    sort_order: record.sort_order
  });
  modalVisible.value = true;
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    modalLoading.value = true;
    
    const payload = {
      name: formData.name,
      subject_id: formData.subject_id,
      description: formData.description,
      sort_order: formData.sort_order
    };

    if (formData.id) {
      await updateKnowledgePoint(formData.id, payload);
      message.success('更新成功');
    } else {
      await createKnowledgePoint(payload);
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
    await deleteKnowledgePoint(record.id);
    message.success('删除成功');
    fetchData();
  } catch (error) {
    console.error(error);
  }
};

onMounted(async () => {
  await fetchGrades();
  
  // Initialize from route query if available (e.g. from SubjectList)
  if (route.query.grade_id) {
      searchParams.grade_id = Number(route.query.grade_id);
      await fetchSubjects(searchParams.grade_id, subjectOptions);
  }
  if (route.query.subject_id) {
      searchParams.subject_id = Number(route.query.subject_id);
  }
  
  fetchData();
});
</script>

<style scoped>
.kp-container {
  min-height: 100%;
}
</style>
