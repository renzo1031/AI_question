<template>
  <div class="correction-list-container">
    <!-- 统计卡片 -->
    <div class="stats-overview">
      <a-card class="stat-card" :bordered="false">
        <div class="stat-content">
          <div class="stat-icon error-bg">
            <clock-circle-outlined />
          </div>
          <div class="stat-info">
            <div class="stat-title">待处理纠错</div>
            <div class="stat-value error-text">{{ stats.pending_count || 0 }}</div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 搜索栏 -->
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="状态">
          <a-select v-model:value="searchParams.status" placeholder="全部" style="width: 120px" allow-clear>
            <a-select-option value="pending">待处理</a-select-option>
            <a-select-option value="resolved">已解决</a-select-option>
            <a-select-option value="ignored">已忽略</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="题目ID">
          <a-input-number v-model:value="searchParams.question_id" placeholder="题目ID" style="width: 150px" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 列表 -->
    <a-card title="纠错列表" :bordered="false" style="margin-top: 24px">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="pagination"
        :loading="loading"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          
          <template v-else-if="column.dataIndex === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>

          <template v-else-if="column.key === 'action'">
            <span v-if="record.status === 'pending'">
              <a @click="openHandleModal(record, 'resolved')">解决</a>
              <a-divider type="vertical" />
              <a @click="openHandleModal(record, 'ignored')">忽略</a>
            </span>
            <span v-else>-</span>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 处理弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      :confirmLoading="modalLoading"
    >
      <a-form :model="formData" layout="vertical">
        <a-form-item label="处理备注">
          <a-textarea v-model:value="formData.admin_note" :rows="4" placeholder="请输入处理备注（可选）" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { ClockCircleOutlined } from '@ant-design/icons-vue';
import { getCorrections, handleCorrection, getCorrectionStats } from '../api/correction';

const loading = ref(false);
const dataSource = ref([]);
const stats = reactive({
  pending_count: 0
});

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
});

const searchParams = reactive({
  status: undefined,
  question_id: undefined
});

const columns = [
  { title: '题目ID', dataIndex: 'question_id', width: 100 },
  { title: '用户ID', dataIndex: 'user_id', width: 100 },
  { title: '纠错内容', dataIndex: 'content', ellipsis: true },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '管理员备注', dataIndex: 'admin_note', ellipsis: true },
  { title: '提交时间', dataIndex: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchParams
    };
    
    // Clean params
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    const res = await getCorrections(params);
    if (res.code === 0) {
      dataSource.value = res.data.items || [];
      pagination.total = res.data.total || 0;
    } else {
      message.error(res.message || '获取列表失败');
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const fetchStats = async () => {
  try {
    const res = await getCorrectionStats();
    if (res.code === 0) {
      // Assuming res.data contains pending_count or is a number
      if (typeof res.data === 'object') {
        stats.pending_count = res.data.pending_count || res.data.pending || 0;
      } else {
        stats.pending_count = res.data; // If it returns just a number or similar structure
      }
    }
  } catch (error) {
    console.error(error);
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
  searchParams.status = undefined;
  searchParams.question_id = undefined;
  handleSearch();
};

// Handle Modal
const modalVisible = ref(false);
const modalLoading = ref(false);
const currentRecord = ref(null);
const targetStatus = ref('');
const modalTitle = ref('');
const formData = reactive({
  admin_note: ''
});

const openHandleModal = (record, status) => {
  currentRecord.value = record;
  targetStatus.value = status;
  modalTitle.value = status === 'resolved' ? '解决纠错' : '忽略纠错';
  formData.admin_note = '';
  modalVisible.value = true;
};

const handleModalOk = async () => {
  modalLoading.value = true;
  try {
    const res = await handleCorrection(currentRecord.value.id, {
      status: targetStatus.value,
      admin_note: formData.admin_note
    });
    
    if (res.code === 0) {
      message.success('操作成功');
      modalVisible.value = false;
      fetchData();
      fetchStats();
    } else {
      message.error(res.message || '操作失败');
    }
  } catch (error) {
    console.error(error);
  } finally {
    modalLoading.value = false;
  }
};

const getStatusColor = (status) => {
  const map = {
    pending: 'orange',
    resolved: 'green',
    ignored: 'gray'
  };
  return map[status] || 'default';
};

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    resolved: '已解决',
    ignored: '已忽略'
  };
  return map[status] || status;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchData();
  fetchStats();
});
</script>

<style scoped>
.correction-list-container {
  min-height: 100%;
}
.stats-overview {
  margin-bottom: 24px;
}
.stat-card {
  width: 300px;
  border-radius: 8px;
  transition: all 0.3s;
  overflow: hidden;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.stat-content {
  display: flex;
  align-items: center;
  padding: 12px 0;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
  flex-shrink: 0;
}
.error-bg {
  background: #fff1f0;
  color: #ff4d4f;
}
.stat-info {
  flex: 1;
  overflow: hidden;
}
.stat-title {
  color: #8c8c8c;
  font-size: 14px;
  margin-bottom: 4px;
}
.stat-value {
  color: #000000d9;
  font-size: 24px;
  font-weight: 600;
  line-height: 1;
}
.error-text {
  color: #ff4d4f;
}
.search-card {
  margin-bottom: 24px;
  border-radius: 8px;
}
</style>
