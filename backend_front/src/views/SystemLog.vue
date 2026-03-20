<template>
  <div class="system-log-container">
    <!-- 统计卡片 -->
    <a-row :gutter="16" class="stats-row">
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon primary-bg">
              <file-text-outlined />
            </div>
            <div class="stat-info">
              <div class="stat-title">日志总数</div>
              <div class="stat-value">{{ stats.total || 0 }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon error-bg">
              <close-circle-outlined />
            </div>
            <div class="stat-info">
              <div class="stat-title">错误日志</div>
              <div class="stat-value error-text">{{ stats.error_count || 0 }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon warning-bg">
              <warning-outlined />
            </div>
            <div class="stat-info">
              <div class="stat-title">警告日志</div>
              <div class="stat-value warning-text">{{ stats.warning_count || 0 }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card cleanup-card" :bordered="false">
          <div class="cleanup-wrapper">
            <div class="cleanup-icon">
               <delete-outlined />
            </div>
            <div class="cleanup-info">
               <div class="cleanup-title">日志清理</div>
               <a-popconfirm
                title="确定要清理30天前的日志吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleCleanup"
              >
                <a-button type="primary" danger size="small" :loading="cleanupLoading" ghost style="display: flex; align-items: center; justify-content: center;">
                  清理30天前日志
                </a-button>
              </a-popconfirm>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 日志列表 -->
    <a-card :bordered="false" style="margin-top: 24px">
      <template #title>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span>日志列表</span>
          <a-space>
            <a-button 
              type="link" 
              @click="handleRefresh" 
              :loading="loading"
              style="padding: 0; height: auto"
            >
              <template #icon><reload-outlined /></template>
              刷新
            </a-button>
            <a-divider type="vertical" />
            <a-button 
              type="link" 
              @click="showSearch = !showSearch" 
              style="padding: 0; height: auto"
            >
              <template #icon><filter-outlined /></template>
              筛选
            </a-button>
          </a-space>
        </div>
      </template>
      
      <!-- 搜索表单 -->
      <div v-show="showSearch" style="margin-bottom: 24px; background: #f8f9fa; padding: 24px; border-radius: 8px; border: 1px solid #f0f0f0;">
        <a-form layout="vertical" :model="searchParams" @finish="handleSearch">
          <a-row :gutter="24">
            <a-col :span="6">
              <a-form-item label="关键词">
                <a-input v-model:value="searchParams.action" placeholder="搜索动作/描述" allow-clear>
                  <template #prefix><search-outlined style="color: rgba(0,0,0,.25)"/></template>
                </a-input>
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item label="模块">
                <a-input v-model:value="searchParams.module" placeholder="模块名称" allow-clear />
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item label="用户名">
                <a-input v-model:value="searchParams.username" placeholder="用户名" allow-clear>
                   <template #prefix><user-outlined style="color: rgba(0,0,0,.25)"/></template>
                </a-input>
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item label="日志级别">
                <a-select v-model:value="searchParams.log_level" placeholder="全部" allow-clear style="width: 100%">
                  <a-select-option value="DEBUG"><a-tag color="default">DEBUG</a-tag></a-select-option>
                  <a-select-option value="INFO"><a-tag color="blue">INFO</a-tag></a-select-option>
                  <a-select-option value="WARNING"><a-tag color="orange">WARNING</a-tag></a-select-option>
                  <a-select-option value="ERROR"><a-tag color="red">ERROR</a-tag></a-select-option>
                  <a-select-option value="CRITICAL"><a-tag color="purple">CRITICAL</a-tag></a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="时间范围">
                <a-range-picker 
                  v-model:value="dateRange" 
                  :show-time="{ format: 'HH:mm' }" 
                  format="YYYY-MM-DD HH:mm"
                  :placeholder="['开始时间', '结束时间']"
                  @change="handleDateChange"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12" style="text-align: right; display: flex; align-items: flex-end; justify-content: flex-end; margin-bottom: 24px;">
              <a-space>
                <a-button type="primary" html-type="submit" :loading="loading">
                  <template #icon><search-outlined /></template>
                  查询
                </a-button>
                <a-button @click="handleReset">
                  <template #icon><reload-outlined /></template>
                  重置
                </a-button>
              </a-space>
            </a-col>
          </a-row>
        </a-form>
      </div>

      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="false"
        :loading="loading"
        row-key="id"
        size="middle"
        class="custom-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'log_level'">
            <a-tag :color="getLevelColor(record.log_level)">
              {{ record.log_level }}
            </a-tag>
          </template>
          
          <template v-else-if="column.dataIndex === 'request_info'">
            <div v-if="record.request_method">
              <a-tag>{{ record.request_method }}</a-tag>
              <span style="font-family: monospace">{{ record.request_path }}</span>
            </div>
            <span v-else>-</span>
          </template>

          <template v-else-if="column.dataIndex === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>

          <template v-else-if="column.key === 'action_btn'">
            <a @click="showDetail(record)">详情</a>
          </template>
        </template>
      </a-table>

      <div class="pagination-container">
        <a-pagination
          v-model:current="pagination.current"
          v-model:pageSize="pagination.pageSize"
          :total="pagination.total"
          :show-less-items="true"
          :show-size-changer="pagination.showSizeChanger"
          :page-size-options="pagination.pageSizeOptions"
          @change="handlePaginationChange"
          :show-total="total => `共 ${total} 条`"
        />
      </div>
    </a-card>

    <!-- 详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="日志详情"
      width="800px"
      :footer="null"
    >
      <a-spin :spinning="detailLoading">
        <a-descriptions bordered :column="1" size="small">
          <a-descriptions-item label="日志ID">{{ currentLog?.id }}</a-descriptions-item>
          <a-descriptions-item label="时间">{{ formatDate(currentLog?.created_at) }}</a-descriptions-item>
          <a-descriptions-item label="级别">
            <a-tag :color="getLevelColor(currentLog?.log_level)">{{ currentLog?.log_level }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="模块">{{ currentLog?.module }}</a-descriptions-item>
          <a-descriptions-item label="动作">{{ currentLog?.action }}</a-descriptions-item>
          <a-descriptions-item label="用户ID">{{ currentLog?.user_id || '-' }}</a-descriptions-item>
          <a-descriptions-item label="用户名">{{ currentLog?.username || '-' }}</a-descriptions-item>
          <a-descriptions-item label="用户类型">{{ currentLog?.user_type || '-' }}</a-descriptions-item>
          <a-descriptions-item label="IP地址">{{ currentLog?.ip_address || '-' }}</a-descriptions-item>
          <a-descriptions-item label="User Agent">
            <div style="word-break: break-all; max-height: 100px; overflow-y: auto;">{{ currentLog?.user_agent || '-' }}</div>
          </a-descriptions-item>
          <a-descriptions-item label="请求信息">
            <span v-if="currentLog?.request_method">
              [{{ currentLog.request_method }}] {{ currentLog.request_path }}
            </span>
            <span v-else>-</span>
          </a-descriptions-item>
          <a-descriptions-item label="请求参数" v-if="currentLog?.request_params && Object.keys(currentLog.request_params).length">
            <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; max-height: 200px; overflow: auto;">{{ JSON.stringify(currentLog.request_params, null, 2) }}</pre>
          </a-descriptions-item>
          <a-descriptions-item label="状态码">{{ currentLog?.status_code || '-' }}</a-descriptions-item>
          <a-descriptions-item label="是否成功">
            <a-tag :color="currentLog?.is_success ? 'success' : 'error'">
              {{ currentLog?.is_success ? '成功' : '失败' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="响应时间">{{ currentLog?.response_time_ms ? currentLog.response_time_ms + 'ms' : '-' }}</a-descriptions-item>
          <a-descriptions-item label="描述">
            <div style="white-space: pre-wrap; word-break: break-all;">{{ currentLog?.description }}</div>
          </a-descriptions-item>
          <a-descriptions-item label="错误信息" v-if="currentLog?.error_message">
            <div style="color: red; white-space: pre-wrap; word-break: break-all;">{{ currentLog?.error_message }}</div>
          </a-descriptions-item>
          <a-descriptions-item label="额外信息" v-if="currentLog?.extra_data && Object.keys(currentLog.extra_data).length">
            <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; max-height: 200px; overflow: auto;">{{ JSON.stringify(currentLog.extra_data, null, 2) }}</pre>
          </a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, onUnmounted, onDeactivated } from 'vue';
import { message } from 'ant-design-vue';
import { 
  FileTextOutlined, 
  CloseCircleOutlined, 
  WarningOutlined, 
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
  FilterOutlined
} from '@ant-design/icons-vue';
import { getSystemLogs, getLogStatistics, cleanLogs, getLogDetail } from '../api/log';

const loading = ref(false);
const cleanupLoading = ref(false);
const dataSource = ref([]);
const dateRange = ref([]);
const showSearch = ref(false);
const stats = reactive({
  total: 0,
  error_count: 0,
  warning_count: 0
});

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['20', '50', '100', '200']
});

const searchParams = reactive({
  action: '',
  log_level: undefined,
  module: '',
  username: '',
  start_time: undefined,
  end_time: undefined
});

const columns = [
  {
    title: '级别',
    dataIndex: 'log_level',
    key: 'log_level',
    width: 100,
  },
  {
    title: '请求',
    dataIndex: 'request_method',
    key: 'request_method',
    width: 100,
  },
  {
    title: '动作',
    dataIndex: 'action',
    key: 'action',
    width: 150,
    ellipsis: true,
  },
  {
    title: '用户ID',
    dataIndex: 'user_id',
    key: 'user_id',
    width: 150,
    ellipsis: true,
  },
  {
    title: 'IP',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 140,
  },
  {
    title: '时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: '操作',
    key: 'action_btn',
    width: 80,
    fixed: 'right',
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
    
    // Remove undefined params
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    const res = await getSystemLogs(params);
    if (res.code === 0) {
      dataSource.value = res.data.items || [];
      pagination.total = res.data.total || 0;
    } else {
      message.error(res.message || '获取日志失败');
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const fetchStatistics = async () => {
  try {
    const params = {};
    if (searchParams.start_time) params.start_time = searchParams.start_time;
    if (searchParams.end_time) params.end_time = searchParams.end_time;
    
    const res = await getLogStatistics(params);
    if (res.code === 0) {
      const data = res.data || {};
      
      // 适配实际 API 返回结构
      // 总日志数
      stats.total = data.total ?? 0;
      
      // 各日志级别日志数
      // 实际字段名: by_log_level
      const levelStats = data.by_log_level || {};
      
      // 错误日志 (ERROR + CRITICAL)
      stats.error_count = (levelStats.ERROR || 0) + (levelStats.CRITICAL || 0);
                         
      // 警告日志 (WARNING)
      stats.warning_count = (levelStats.WARNING || 0);
    }
  } catch (error) {
    console.error(error);
  }
};

const handlePaginationChange = (page, pageSize) => {
  const nextPageSize = pageSize ?? pagination.pageSize;
  const isPageSizeChange = nextPageSize !== pagination.pageSize;
  pagination.pageSize = nextPageSize;
  pagination.current = isPageSizeChange ? 1 : page;
  fetchData();
};

const handleSearch = () => {
  pagination.current = 1;
  fetchData();
  fetchStatistics();
};

const handleReset = () => {
  searchParams.action = '';
  searchParams.log_level = undefined;
  searchParams.module = '';
  searchParams.username = '';
  searchParams.start_time = undefined;
  searchParams.end_time = undefined;
  dateRange.value = [];
  handleSearch();
};

const handleDateChange = (dates) => {
  if (dates) {
    searchParams.start_time = dates[0].toISOString();
    searchParams.end_time = dates[1].toISOString();
  } else {
    searchParams.start_time = undefined;
    searchParams.end_time = undefined;
  }
};

const getLevelColor = (level) => {
  const colors = {
    'DEBUG': 'default',
    'INFO': 'blue',
    'WARNING': 'orange',
    'ERROR': 'red',
    'CRITICAL': 'purple'
  };
  return colors[level] || 'default';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

// Detail Modal
const detailModalVisible = ref(false);
const detailLoading = ref(false);
const currentLog = ref(null);

const showDetail = async (record) => {
  currentLog.value = record;
  detailModalVisible.value = true;
  detailLoading.value = true;
  try {
    const res = await getLogDetail(record.id);
    if (res.code === 0) {
      currentLog.value = res.data;
    } else {
      message.warning('获取完整详情失败，显示列表数据');
    }
  } catch (error) {
    console.error(error);
  } finally {
    detailLoading.value = false;
  }
};

// Cleanup
const handleCleanup = async () => {
  cleanupLoading.value = true;
  try {
    const res = await cleanLogs(30); // 默认清理30天前
    if (res.code === 0) {
      message.success(res.message || '清理成功');
      fetchData(); // Refresh list
      fetchStatistics(); // Refresh stats
    } else {
      message.error(res.message || '清理失败');
    }
  } catch (error) {
    console.error(error);
    message.error('清理请求失败');
  } finally {
    cleanupLoading.value = false;
  }
};

const handleRefresh = () => {
  fetchData();
  fetchStatistics();
};

let timer = null;

const startAutoRefresh = () => {
  stopAutoRefresh();
  timer = setInterval(() => {
    handleRefresh();
  }, 60000);
};

const stopAutoRefresh = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
};

onMounted(() => {
  fetchData();
  fetchStatistics();
  startAutoRefresh();
});

onActivated(() => {
  fetchData();
  fetchStatistics();
  startAutoRefresh();
});

onUnmounted(() => {
  stopAutoRefresh();
});

onDeactivated(() => {
  stopAutoRefresh();
});
</script>

<style scoped>
.system-log-container {
  min-height: 100%;
}
.stats-row {
  margin-bottom: 24px;
}

/* 统计卡片样式 */
.stat-card {
  height: 100%;
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
.primary-bg {
  background: #e6f7ff;
  color: #1890ff;
}
.error-bg {
  background: #fff1f0;
  color: #ff4d4f;
}
.warning-bg {
  background: #fffbe6;
  color: #faad14;
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
.warning-text {
  color: #faad14;
}

/* 清理卡片特殊样式 */
.cleanup-card :deep(.ant-card-body) {
  padding: 24px;
  height: 100%;
  display: flex;
  align-items: center;
}
.cleanup-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
}
.cleanup-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #fff0f6;
  color: #eb2f96;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
  flex-shrink: 0;
}
.cleanup-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.cleanup-title {
  color: #8c8c8c;
  font-size: 14px;
  margin-bottom: 4px;
}

.search-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

/* 自定义分页样式 - 重构版 */
.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  padding: 10px 24px;
  background: #fafafa;
  border-radius: 50px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid #f0f0f0;
}

.pagination-container :deep(.ant-pagination) {
  margin: 0;
  display: flex;
  align-items: center;
}

.pagination-container :deep(.ant-pagination-item),
.pagination-container :deep(.ant-pagination-prev .ant-pagination-item-link),
.pagination-container :deep(.ant-pagination-next .ant-pagination-item-link) {
  border: none;
  background: transparent;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s;
}

.pagination-container :deep(.ant-pagination-item:hover),
.pagination-container :deep(.ant-pagination-prev:hover .ant-pagination-item-link),
.pagination-container :deep(.ant-pagination-next:hover .ant-pagination-item-link) {
  background: #e6f7ff;
  color: #1890ff;
}

.pagination-container :deep(.ant-pagination-item-active) {
  background: #1890ff;
  color: #fff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.25);
}

.pagination-container :deep(.ant-pagination-item-active a) {
  color: #fff !important;
}

.pagination-container :deep(.ant-pagination-options) {
  margin-left: 16px;
}

.pagination-container :deep(.ant-pagination-total-text) {
  margin-right: 16px;
  color: #8c8c8c;
  font-size: 13px;
}
</style>
