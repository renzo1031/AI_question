<template>
  <div class="question-list-container">
    <a-card title="题库列表" :bordered="false">
      <template #extra>
        <a-space>
          <a-button @click="showFilter = !showFilter">
            <FilterOutlined /> 筛选
          </a-button>
          <a-button type="primary" @click="handleAdd">新增题目</a-button>
          <a-button @click="handleImport">批量导入</a-button>
        </a-space>
      </template>

      <div v-show="showFilter" style="margin-bottom: 24px; padding: 24px; background: #fbfbfb; border: 1px solid #eee; border-radius: 4px;">
        <a-form layout="inline" :model="searchParams" @finish="handleSearch">
          <a-form-item label="题目ID" style="margin-bottom: 16px;">
            <a-input-number v-model:value="searchParams.question_id" placeholder="ID" style="width: 100px" :min="1" />
          </a-form-item>
          <a-form-item label="年级" style="margin-bottom: 16px;">
            <a-select
              v-model:value="searchParams.grade_id"
              placeholder="选择年级"
              style="width: 120px"
              allow-clear
              :options="gradeOptions"
              :field-names="{ label: 'name', value: 'id' }"
              @change="handleSearchGradeChange"
            />
          </a-form-item>
          <a-form-item label="学科" style="margin-bottom: 16px;">
            <a-select
              v-model:value="searchParams.subject_id"
              placeholder="选择学科"
              style="width: 150px"
              allow-clear
              :options="searchSubjectOptions"
              :field-names="{ label: 'name', value: 'id' }"
              :disabled="!searchParams.grade_id"
              @change="handleSearchSubjectChange"
            />
          </a-form-item>
          <a-form-item label="知识点" style="margin-bottom: 16px;">
            <a-select
              v-model:value="searchParams.knowledge_point_id"
              placeholder="选择知识点"
              style="width: 150px"
              allow-clear
              :options="searchKnowledgeOptions"
              :field-names="{ label: 'name', value: 'id' }"
              :disabled="!searchParams.subject_id"
              show-search
              :filter-option="filterOption"
            />
          </a-form-item>
          <a-form-item label="类型" style="margin-bottom: 16px;">
            <a-select v-model:value="searchParams.question_type" placeholder="全部" style="width: 120px" allow-clear>
              <a-select-option value="single_choice">单选题</a-select-option>
              <a-select-option value="multiple_choice">多选题</a-select-option>
              <a-select-option value="fill_blank">填空题</a-select-option>
              <a-select-option value="short_answer">简答题</a-select-option>
              <a-select-option value="calculation">计算题</a-select-option>
              <a-select-option value="proof">证明题</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="难度" style="margin-bottom: 16px;">
            <a-select v-model:value="searchParams.difficulty" placeholder="全部" style="width: 120px" allow-clear>
              <a-select-option v-for="i in 10" :key="i" :value="i">{{ i }}</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="关键词" style="margin-bottom: 16px;">
            <a-input v-model:value="searchParams.keyword" placeholder="题目内容" allow-clear />
          </a-form-item>
          <a-form-item style="margin-bottom: 16px;">
            <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
            <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
          </a-form-item>
        </a-form>
      </div>
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="pagination"
        :loading="loading"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'question_type'">
            <a-tag v-if="record.question_type === 'single_choice' || record.question_type === '选择题'">单选题</a-tag>
            <a-tag v-else-if="record.question_type === 'multiple_choice' || record.question_type === '多选题'">多选题</a-tag>
            <a-tag v-else-if="record.question_type === 'fill_blank' || record.question_type === '填空题'">填空题</a-tag>
            <a-tag v-else-if="record.question_type === 'short_answer' || record.question_type === '简答题'">简答题</a-tag>
            <a-tag v-else>{{ record.question_type }}</a-tag>
          </template>

          <template v-else-if="column.dataIndex === 'grade'">
            <a-tag :color="getGradeColor(record.grade)">{{ record.grade }}</a-tag>
          </template>

          <template v-else-if="column.dataIndex === 'difficulty'">
            <a-tag :color="getDifficultyColor(record.difficulty)">{{ record.difficulty }}</a-tag>
          </template>

          <template v-else-if="column.dataIndex === 'content'">
            <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              {{ record.content }}
            </div>
          </template>

          <template v-else-if="column.dataIndex === 'knowledge_points'">
             <span>{{ record.knowledge_point || '-' }}</span>
          </template>

          <template v-else-if="column.dataIndex === 'action'">
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm title="确定删除该题目吗？" @confirm="handleDelete(record.id)">
               <a style="color: red">删除</a>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      :confirmLoading="modalLoading"
      width="800px"
    >
      <a-form :model="formData" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }" ref="formRef">
        
        <a-form-item label="年级" name="grade_id" :rules="[{ required: true, message: '请选择年级' }]">
           <a-select
             v-model:value="formData.grade_id"
             placeholder="请选择年级"
             :options="gradeOptions"
             :field-names="{ label: 'name', value: 'id' }"
             @change="handleModalGradeChange"
           />
        </a-form-item>

        <a-form-item label="学科" name="subject_id" :rules="[{ required: true, message: '请选择学科' }]">
          <a-select 
            v-model:value="formData.subject_id"
            placeholder="请选择学科"
            :options="modalSubjectOptions"
            :field-names="{ label: 'name', value: 'id' }"
            :disabled="!formData.grade_id"
            @change="handleModalSubjectChange"
          />
        </a-form-item>
        
        <a-form-item label="知识点" name="knowledge_point_id">
          <a-select
            v-model:value="formData.knowledge_point_id"
            placeholder="请选择知识点"
            :options="modalKnowledgeOptions"
            :field-names="{ label: 'name', value: 'id' }"
            :disabled="!formData.subject_id"
            show-search
            :filter-option="filterOption"
            @change="handleModalKnowledgeChange"
          />
        </a-form-item>

        <a-form-item label="类型" name="question_type" :rules="[{ required: true, message: '请选择类型' }]">
          <a-select v-model:value="formData.question_type">
            <a-select-option value="single_choice">单选题</a-select-option>
            <a-select-option value="multiple_choice">多选题</a-select-option>
            <a-select-option value="fill_blank">填空题</a-select-option>
            <a-select-option value="short_answer">简答题</a-select-option>
            <a-select-option value="calculation">计算题</a-select-option>
            <a-select-option value="proof">证明题</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="难度" name="difficulty" :rules="[{ required: true, message: '请选择难度' }]">
          <a-select v-model:value="formData.difficulty">
            <a-select-option v-for="i in 10" :key="i" :value="i">{{ i }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="题目内容" name="content" :rules="[{ required: true, message: '请输入题目内容' }]">
          <a-textarea v-model:value="formData.content" :rows="4" />
        </a-form-item>

        <div v-if="['single_choice', 'multiple_choice'].includes(formData.question_type)">
           <a-form-item label="选项" :rules="[{ required: true, message: '请输入选项' }]">
             <div v-for="(opt, idx) in formData.options" :key="idx" style="margin-bottom: 8px; display: flex; align-items: center;">
               <a-input v-model:value="opt.option_key" style="width: 60px; margin-right: 8px;" placeholder="Key" />
               <a-input v-model:value="opt.option_text" placeholder="选项内容" />
               <a-button type="link" danger @click="removeOption(idx)" v-if="formData.options.length > 2">删除</a-button>
             </div>
             <a-button type="dashed" block @click="addOption">添加选项</a-button>
           </a-form-item>
        </div>

        <a-form-item label="AI答案" name="ai_answer">
          <a-input v-if="!['single_choice', 'multiple_choice'].includes(formData.question_type)" v-model:value="formData.ai_answer" />
          <a-select v-else v-model:value="formData.ai_answer" :mode="formData.question_type === 'multiple_choice' ? 'multiple' : undefined">
            <a-select-option v-for="(opt, idx) in formData.options" :key="idx" :value="opt.option_key">
              {{ opt.option_key }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="AI解析" name="ai_analysis">
          <a-textarea v-model:value="formData.ai_analysis" :rows="3" />
        </a-form-item>
        
        <a-form-item label="来源" name="source">
          <a-input v-model:value="formData.source" />
        </a-form-item>
        
        <!-- Grade is now handled at the top -->
      </a-form>
    </a-modal>
    
    <!-- Import Modal -->
    <a-modal
      v-model:open="importVisible"
      title="批量导入题目"
      @ok="handleImportOk"
      :confirmLoading="importLoading"
      width="600px"
    >
      <a-tabs default-active-key="1">
        <a-tab-pane key="1" tab="JSON文本导入">
          <a-alert message="请粘贴符合格式的JSON数组，例如：[{ 'content': '...', 'type': 'single_choice', ... }]" type="info" show-icon style="margin-bottom: 16px" />
          <a-textarea
            v-model:value="importJson"
            placeholder="在此粘贴JSON数据..."
            :rows="10"
          />
        </a-tab-pane>
        <a-tab-pane key="2" tab="文件上传">
           <a-upload-dragger
            name="file"
            :multiple="false"
            :before-upload="beforeUpload"
            accept=".json"
            :show-upload-list="false"
          >
            <p class="ant-upload-drag-icon">
              <inbox-outlined />
            </p>
            <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p class="ant-upload-hint">
              仅支持 .json 文件
            </p>
          </a-upload-dragger>
          <div v-if="uploadedFileName" style="margin-top: 16px; text-align: center; color: #1890ff;">
            <file-text-outlined /> {{ uploadedFileName }}
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { InboxOutlined, FileTextOutlined } from '@ant-design/icons-vue';
import { getQuestionList, createQuestion, updateQuestion, deleteQuestion, importQuestions } from '../api/question';
import { getSubjectList, getKnowledgePointsBySubject } from '../api/subject';
import { getGradeList, getAllGrades, getSubjectsByGrade } from '../api/grade';

const showFilter = ref(false);
const loading = ref(false);
const dataSource = ref([]);
const subjects = ref([]);
const gradeOptions = ref([]);
const modalSubjectOptions = ref([]);
const modalKnowledgeOptions = ref([]);
const searchSubjectOptions = ref([]);
const searchKnowledgeOptions = ref([]);

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
});

const searchParams = reactive({
  question_id: undefined,
  grade_id: undefined,
  subject_id: undefined,
  knowledge_point_id: undefined,
  question_type: undefined,
  difficulty: undefined,
  keyword: ''
});

const getDifficultyColor = (difficulty) => {
  if (difficulty <= 3) return 'green';
  if (difficulty <= 6) return 'blue';
  if (difficulty <= 8) return 'orange';
  return 'red';
};

const getGradeColor = (grade) => {
  if (!grade) return 'default';
  const colors = ['pink', 'red', 'orange', 'green', 'cyan', 'blue', 'purple', 'geekblue', 'magenta', 'volcano', 'gold', 'lime'];
  let hash = 0;
  for (let i = 0; i < grade.length; i++) {
    hash = grade.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colors.length;
  return colors[index];
};

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
  },
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content',
    width: 300,
  },
  {
    title: '年级',
    dataIndex: 'grade',
    key: 'grade',
  },
  {
    title: '学科',
    dataIndex: 'subject', // API returns subject name as string
    key: 'subject',
  },
  {
    title: '类型',
    dataIndex: 'question_type',
    key: 'question_type',
  },
  {
    title: '难度',
    dataIndex: 'difficulty',
    key: 'difficulty',
  },
  {
    title: '知识点',
    dataIndex: 'knowledge_point',
    key: 'knowledge_point',
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 150,
  },
];

const fetchSubjects = async () => {
  try {
    const res = await getSubjectList({ page: 1, page_size: 200 });
    subjects.value = res.data || [];
  } catch (e) {
    console.error(e);
  }
};

const fetchGrades = async () => {
  try {
    const res = await getAllGrades();
    gradeOptions.value = res.data || [];
  } catch (e) {
    console.error(e);
  }
};

const fetchModalSubjects = async (gradeId) => {
    if (!gradeId) {
        modalSubjectOptions.value = [];
        return;
    }
    try {
        const res = await getSubjectsByGrade(gradeId, { page: 1, page_size: 200 });
        modalSubjectOptions.value = res.data || [];
    } catch (e) {
        console.error(e);
    }
};

const fetchModalKnowledgePoints = async (subjectId) => {
    if (!subjectId) {
        modalKnowledgeOptions.value = [];
        return;
    }
    try {
        const res = await getKnowledgePointsBySubject(subjectId, { page: 1, page_size: 200 });
        modalKnowledgeOptions.value = res.data || [];
    } catch (e) {
        console.error(e);
    }
};

const fetchSearchSubjects = async (gradeId) => {
    if (!gradeId) {
        searchSubjectOptions.value = [];
        return;
    }
    try {
        const res = await getSubjectsByGrade(gradeId, { page: 1, page_size: 200 });
        searchSubjectOptions.value = res.data || [];
    } catch (e) {
        console.error(e);
    }
};

const fetchSearchKnowledgePoints = async (subjectId) => {
    if (!subjectId) {
        searchKnowledgeOptions.value = [];
        return;
    }
    try {
        const res = await getKnowledgePointsBySubject(subjectId, { page: 1, page_size: 200 });
        searchKnowledgeOptions.value = res.data || [];
    } catch (e) {
        console.error(e);
    }
};

const handleSearchGradeChange = (val) => {
    searchParams.subject_id = undefined;
    searchParams.knowledge_point_id = undefined;
    fetchSearchSubjects(val);
};

const handleSearchSubjectChange = (val) => {
    searchParams.knowledge_point_id = undefined;
    fetchSearchKnowledgePoints(val);
};

const handleModalGradeChange = (val) => {
    formData.subject_id = undefined;
    formData.subject = '';
    formData.knowledge_point_id = undefined;
    formData.knowledge_point = '';
    fetchModalSubjects(val);
    
    const grade = gradeOptions.value.find(g => g.id === val);
    if (grade) {
        formData.grade = grade.name;
    }
};

const handleModalSubjectChange = (val) => {
    formData.knowledge_point_id = undefined;
    formData.knowledge_point = '';
    fetchModalKnowledgePoints(val);
    
    const sub = modalSubjectOptions.value.find(s => s.id === val);
    if (sub) {
        formData.subject = sub.name;
    }
};

const handleModalKnowledgeChange = (val) => {
    const kp = modalKnowledgeOptions.value.find(k => k.id === val);
    if (kp) {
        formData.knowledge_point = kp.name;
    }
};

const filterOption = (input, option) => {
  return option.name.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

const fetchData = async () => {
  loading.value = true;
  try {
    // Construct params object for API
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
    };
    
    // Add optional search params only if they have values
    if (searchParams.question_id) params.question_id = searchParams.question_id;
    
    if (searchParams.grade_id) {
       const grade = gradeOptions.value.find(g => g.id === searchParams.grade_id);
       if (grade) params.grade = grade.name;
    }

    if (searchParams.subject_id) {
       // Try to find in searchSubjectOptions first, then fall back to all subjects if needed
       let sub = searchSubjectOptions.value.find(s => s.id === searchParams.subject_id);
       if (!sub) sub = subjects.value.find(s => s.id === searchParams.subject_id);
       if (sub) params.subject = sub.name;
    }
    
    if (searchParams.knowledge_point_id) {
       const kp = searchKnowledgeOptions.value.find(k => k.id === searchParams.knowledge_point_id);
       if (kp) params.knowledge_point = kp.name;
    }
    
    if (searchParams.question_type) params.question_type = searchParams.question_type;
    if (searchParams.difficulty) params.difficulty = searchParams.difficulty;
    if (searchParams.keyword) params.keyword = searchParams.keyword;

    const res = await getQuestionList(params);
    dataSource.value = res.data;
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

const handleSearch = () => {
  pagination.current = 1;
  fetchData();
};

const handleReset = () => {
  Object.assign(searchParams, {
    question_id: undefined,
    grade_id: undefined,
    subject_id: undefined,
    knowledge_point_id: undefined,
    question_type: undefined,
    difficulty: undefined,
    keyword: ''
  });
  handleSearch();
};

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchData();
};

const handleDelete = async (id) => {
  try {
    await deleteQuestion(id);
    message.success('删除成功');
    fetchData();
  } catch (e) {
    console.error(e);
  }
};

// Modal Logic
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalTitle = ref('新增题目');
const formRef = ref(null);

const formData = reactive({
  id: undefined,
  grade_id: undefined, // UI select
  subject_id: undefined, // UI select
  knowledge_point_id: undefined, // UI select
  subject: '', // For API
  knowledge_point: '', // For API
  question_type: 'single_choice',
  difficulty: 5,
  content: '',
  options: [
    { option_key: 'A', option_text: '' },
    { option_key: 'B', option_text: '' },
    { option_key: 'C', option_text: '' },
    { option_key: 'D', option_text: '' }
  ],
  ai_answer: '',
  ai_analysis: '',
  source: '',
  grade: '', // For API
  tag_ids: []
});

const handleAdd = () => {
  modalTitle.value = '新增题目';
  Object.assign(formData, {
    id: undefined,
    grade_id: undefined,
    subject_id: undefined,
    knowledge_point_id: undefined,
    subject: '',
    knowledge_point: '',
    question_type: 'single_choice',
    difficulty: 5,
    content: '',
    options: [
      { option_key: 'A', option_text: '' },
      { option_key: 'B', option_text: '' },
      { option_key: 'C', option_text: '' },
      { option_key: 'D', option_text: '' }
    ],
    ai_answer: '',
    ai_analysis: '',
    source: '',
    grade: '',
    tag_ids: []
  });
  
  modalSubjectOptions.value = [];
  modalKnowledgeOptions.value = [];
  
  modalVisible.value = true;
};

const handleEdit = async (record) => {
  modalTitle.value = '编辑题目';
  // Populate data
  Object.assign(formData, record);
  
  // Try to reverse engineer IDs from Names for UI
  // 1. Grade
  if (record.grade) {
      const g = gradeOptions.value.find(item => item.name === record.grade);
      if (g) {
          formData.grade_id = g.id;
          await fetchModalSubjects(g.id);
      }
  }
  
  // 2. Subject
  if (record.subject) {
      // Use modalSubjectOptions if populated, else try global subjects or fetch all?
      // Since we need to know Grade first, if Grade was found, modalSubjectOptions is ready.
      // If Grade not found (e.g. data inconsistency), we might need to fetch all subjects to find the ID.
      // But let's assume consistency for now or just rely on what we have.
      
      let sub = null;
      if (formData.grade_id) {
          sub = modalSubjectOptions.value.find(s => s.name === record.subject);
      } else {
          // Fallback: try to find in all subjects
          sub = subjects.value.find(s => s.name === record.subject);
          if (sub) {
              // If we found subject but no grade, maybe we can find grade from subject?
              // But subject list in 'subjects' might not have grade_id info if it was simple list.
              // We'll just set subject_id if we found it.
              // Note: if we set subject_id but no grade_id, the subject select might be disabled or empty if it depends on grade.
              // For editing, we might need to relax the "disabled" check or pre-fill correctly.
              // For now, let's just set it.
          }
      }
      
      if (sub) {
          formData.subject_id = sub.id;
          await fetchModalKnowledgePoints(sub.id);
      }
  }
  
  // 3. Knowledge Point
  if (record.knowledge_point && formData.subject_id) {
      const kp = modalKnowledgeOptions.value.find(k => k.name === record.knowledge_point);
      if (kp) {
          formData.knowledge_point_id = kp.id;
      }
  }
  
  // Map Chinese question types to English codes for UI logic
  const typeMap = {
    '选择题': 'single_choice',
    '单选题': 'single_choice',
    '多选题': 'multiple_choice',
    '填空题': 'fill_blank',
    '简答题': 'short_answer',
    '计算题': 'calculation',
    '证明题': 'proof'
  };
  if (record.question_type && typeMap[record.question_type]) {
    formData.question_type = typeMap[record.question_type];
  }

  // Handle tags mapping
  if (record.tags && Array.isArray(record.tags)) {
    // Check if tags are objects or ids. Based on example, it's an array, likely objects.
    // If it's just IDs, this map might fail if we access .id. 
    // Safely handle both.
    formData.tag_ids = record.tags.map(t => (typeof t === 'object' ? t.id : t));
  }
  
  // Parse options from content if options array is empty
  if ((!formData.options || formData.options.length === 0) && record.content) {
    const optionRegex = /\n([A-Z])\.\s*(.*)/g;
    let match;
    const parsedOptions = [];
    let minIndex = record.content.length;
    
    // We need to clone the regex or reset lastIndex if we were reusing it, but here it's fresh.
    // Note: exec with global flag is stateful.
    
    // We iterate manually to find all matches
    let tempRegex = new RegExp(optionRegex);
    while ((match = tempRegex.exec(record.content)) !== null) {
      parsedOptions.push({
        option_key: match[1],
        option_text: match[2].trim()
      });
      if (match.index < minIndex) {
        minIndex = match.index;
      }
    }
    
    if (parsedOptions.length > 0) {
      formData.content = record.content.substring(0, minIndex).trim();
      formData.options = parsedOptions;
    } else {
        // Fallback: create default 4 options if really none found
        formData.options = [
            { option_key: 'A', option_text: '' },
            { option_key: 'B', option_text: '' },
            { option_key: 'C', option_text: '' },
            { option_key: 'D', option_text: '' }
        ];
    }
  } else if (formData.options && formData.options.length > 0 && typeof formData.options[0] === 'string') {
     // Legacy string array support
     formData.options = formData.options.map((txt, idx) => ({
       option_key: String.fromCharCode(65 + idx),
       option_text: txt
     }));
  }
  
  modalVisible.value = true;
};

const addOption = () => {
  const nextKey = String.fromCharCode(65 + formData.options.length);
  formData.options.push({ option_key: nextKey, option_text: '' });
  optionsReindex();
};

const removeOption = (idx) => {
  formData.options.splice(idx, 1);
  optionsReindex();
};

const optionsReindex = () => {
    formData.options.forEach((opt, index) => {
      opt.option_key = String.fromCharCode(65 + index);
    });
}

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    modalLoading.value = true;
    
    // Ensure string fields are set (should be set by change handlers, but double check)
    // Actually, change handlers set them.
    
    const payload = { ...formData };
    delete payload.grade_id;
    delete payload.subject_id;
    delete payload.knowledge_point_id;
    delete payload.id;
    
    // Basic validation for options if choice question
    if (['single_choice', 'multiple_choice'].includes(payload.question_type)) {
       // Filter empty options or process them? 
    }
    
    if (formData.id) {
      await updateQuestion(formData.id, payload);
      message.success('更新成功');
    } else {
      await createQuestion(payload);
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


const importVisible = ref(false);
const importLoading = ref(false);
const importJson = ref('');
const uploadedFileName = ref('');

const handleImport = () => {
  importJson.value = '';
  uploadedFileName.value = '';
  importVisible.value = true;
};

const beforeUpload = (file) => {
  if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
    message.error('只能上传 JSON 文件');
    return false;
  }
  
  const reader = new FileReader();
  reader.readAsText(file);
  reader.onload = () => {
    importJson.value = reader.result;
    uploadedFileName.value = file.name;
    message.success(`已读取文件: ${file.name}`);
  };
  return false; // Prevent default upload
};

const handleImportOk = async () => {
  if (!importJson.value) {
    message.warning('请输入或上传JSON数据');
    return;
  }

  try {
    const data = JSON.parse(importJson.value);
    if (!Array.isArray(data)) {
      message.error('JSON 必须是数组格式');
      return;
    }
    
    importLoading.value = true;
    // Updated to match OpenAPI spec: { items: [...] }
    await importQuestions({ items: data });
    message.success(`成功导入 ${data.length} 条题目`);
    importVisible.value = false;
    fetchData();
  } catch (error) {
    if (error instanceof SyntaxError) {
      message.error('JSON 格式错误，请检查');
    } else {
      message.error(error.message || '导入失败');
    }
    console.error(error);
  } finally {
    importLoading.value = false;
  }
};

onMounted(() => {
  fetchGrades();
  fetchSubjects();
  fetchData();
});
</script>

<style scoped>
.question-list-container {
  min-height: 100%;
}
</style>
