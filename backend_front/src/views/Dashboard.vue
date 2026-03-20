<template>
  <div class="dashboard-container">
    <a-spin :spinning="loading">
      <!-- 欢迎标语 -->
      <div class="welcome-section animate-slide-down">
        <div class="welcome-bg-decoration"></div>
        <div class="welcome-content">
          <h2 class="welcome-title">
            <span class="greeting-text">早安，</span>
            <span class="user-name">{{ userInfo?.name || '管理员' }}</span>
          </h2>
          <p class="welcome-desc">
            欢迎回来！这是今日的运营数据概览，系统运行平稳。
          </p>
          <div v-if="userInfo?.last_login_at" class="last-login-info">
            <ClockCircleOutlined /> 上次登录：{{ formatDate(userInfo.last_login_at) }}
          </div>
        </div>
        <div class="welcome-action">
          <a-button type="primary" size="large" shape="round" class="refresh-btn" @click="fetchDashboardData">
            <template #icon><ReloadOutlined :spin="loading" /></template>
            刷新数据
          </a-button>
        </div>
      </div>

      <!-- 核心指标卡片 -->
      <div class="stat-grid">
        <div 
          v-for="(stat, index) in statCards" 
          :key="stat.key"
          class="stat-card-wrapper animate-fade-in-up"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <a-card :bordered="false" class="stat-card" hoverable>
            <div class="stat-card-body">
              <div class="stat-icon-wrapper" :class="stat.colorClass">
                <component :is="stat.icon" />
              </div>
              <div class="stat-content">
                <div class="stat-title">{{ stat.title }}</div>
                <div class="stat-value">
                  <span class="number">{{ formatNumber(animatedStats[stat.key]) }}</span>
                  <span v-if="stat.suffix" class="suffix">{{ stat.suffix }}</span>
                </div>
              </div>
            </div>
            <!-- 装饰背景 -->
            <div class="stat-card-decoration" :class="stat.colorClass"></div>
          </a-card>
        </div>
      </div>

      <!-- 趋势图表 -->
      <div class="chart-section animate-fade-in-up" style="animation-delay: 0.5s">
        <a-card :bordered="false" class="chart-card">
          <template #title>
            <div class="card-header-title">
              <LineChartOutlined /> 趋势分析
            </div>
          </template>
          <template #extra>
            <div class="chart-actions">
              <span v-if="notes" class="chart-note">
                <info-circle-outlined /> {{ notes }}
              </span>
              <a-radio-group v-model:value="timeRange" button-style="solid" @change="handleTimeRangeChange">
                <a-radio-button value="7d">近7天</a-radio-button>
                <a-radio-button value="15d">近15天</a-radio-button>
                <a-radio-button value="30d">近30天</a-radio-button>
              </a-radio-group>
            </div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </a-card>
      </div>

      <!-- 底部列表区域 -->
      <a-row :gutter="24" class="list-row">
        <!-- 最近注册用户 -->
        <a-col :xs="24" :lg="12" class="animate-fade-in-up" style="animation-delay: 0.6s">
          <a-card 
            :bordered="false" 
            class="list-card"
            :bodyStyle="{ padding: '0 24px 24px' }"
          >
            <template #title>
              <div class="card-header-title">
                <UserAddOutlined /> 最近注册用户
              </div>
            </template>
            <a-list item-layout="horizontal" :data-source="recentUsers">
              <template #renderItem="{ item, index }">
                <a-list-item class="user-list-item" :style="{ animationDelay: `${0.6 + index * 0.05}s` }">
                  <a-list-item-meta>
                    <template #title>
                      <span class="list-item-title">{{ item.nickname || '未命名用户' }}</span>
                      <a-tag v-if="item.phone" color="blue" class="ml-2">{{ item.phone }}</a-tag>
                    </template>
                    <template #description>
                      <span class="list-item-desc">注册于 {{ formatDate(item.created_at) }}</span>
                    </template>
                    <template #avatar>
                      <a-avatar :style="{ backgroundColor: getAvatarColor(index) }" size="large">
                        <template #icon><UserOutlined /></template>
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                  <div class="user-action-tag">New</div>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>

        <!-- 热门知识点 -->
        <a-col :xs="24" :lg="12" class="animate-fade-in-up" style="animation-delay: 0.7s">
          <a-card 
            :bordered="false" 
            class="list-card"
            :bodyStyle="{ padding: '0 24px 24px' }"
          >
            <template #title>
              <div class="card-header-title">
                <FireOutlined /> 热门知识点 (错题榜)
              </div>
            </template>
            <a-list item-layout="horizontal" :data-source="displayHotKnowledgePoints">
              <template #renderItem="{ item, index }">
                <a-list-item class="knowledge-item" :class="{ 'empty-item': item.empty }">
                  <template v-if="!item.empty">
                    <div class="knowledge-content">
                      <div class="knowledge-header">
                        <span class="list-item-title">
                          <span :class="['rank-badge', index < 3 ? `rank-${index + 1}` : '']">{{ index + 1 }}</span>
                          {{ item.name }}
                        </span>
                        <span class="error-rate-text">{{ (item.wrong_rate * 100).toFixed(1) }}% <span class="rate-label">错误率</span></span>
                      </div>
                      <div class="knowledge-progress-wrapper">
                        <a-progress 
                          :percent="Math.round(item.wrong_rate * 100)" 
                          status="exception" 
                          :show-info="false" 
                          size="small"
                          stroke-linecap="round"
                          :stroke-width="8"
                          class="knowledge-progress"
                        />
                      </div>
                      <div class="knowledge-meta-row">
                        <span><FormOutlined /> 答题: {{ item.answer_count }}</span>
                        <a-divider type="vertical" />
                        <span><CloseCircleOutlined /> 错题: {{ item.wrong_count }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="knowledge-content empty-content">
                      <span class="rank-badge empty-rank">{{ index + 1 }}</span>
                      <span class="empty-text">暂无数据</span>
                    </div>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>
      </a-row>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, nextTick, computed, watch } from 'vue';
import { 
  ReloadOutlined, 
  UserOutlined, 
  UserAddOutlined,
  FileTextOutlined, 
  FormOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
  LineChartOutlined,
  FireOutlined,
  CloseCircleOutlined,
  WarningOutlined
} from '@ant-design/icons-vue';
import { getDashboardData } from '../api/dashboard';
import { getCorrectionStats } from '../api/correction';
import { useUserStore } from '../stores/user';
import * as echarts from 'echarts';
import { message } from 'ant-design-vue';

const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);

const loading = ref(false);
const chartRef = ref(null);
const timeRange = ref('7d');
const notes = ref('');

// 动画相关
const animatedStats = reactive({
  total_users: 0,
  new_users: 0,
  active_users: 0,
  answered_questions: 0,
  accuracy: 0,
  pending_corrections: 0
});

const statCards = [
  { 
    key: 'total_users', 
    title: '总用户数', 
    icon: UserOutlined, 
    colorClass: 'total-bg' 
  },
  { 
    key: 'new_users', 
    title: '新增用户', 
    icon: UserAddOutlined, 
    colorClass: 'new-bg' 
  },
  { 
    key: 'active_users', 
    title: '活跃用户', 
    icon: TeamOutlined, 
    colorClass: 'active-bg' 
  },
  { 
    key: 'answered_questions', 
    title: '已答题目', 
    icon: FormOutlined, 
    colorClass: 'practice-bg' 
  },
  { 
    key: 'accuracy', 
    title: '答题正确率', 
    icon: CheckCircleOutlined, 
    colorClass: 'accuracy-bg',
    suffix: '%'
  },
  {
    key: 'pending_corrections',
    title: '待处理纠错',
    icon: WarningOutlined,
    colorClass: 'correction-bg'
  }
];

const chartData = reactive({
  days: [],
  new_users: [],
  active_users: [],
  answered_questions: [],
  accuracy: []
});

const recentUsers = ref([]);
const hotKnowledgePoints = ref([]);

const displayHotKnowledgePoints = computed(() => {
  const list = [...hotKnowledgePoints.value];
  const targetLength = 5;
  while (list.length < targetLength) {
    list.push({ empty: true, id: `empty-${list.length}` });
  }
  return list.slice(0, targetLength);
});

let chartInstance = null;

// 数字动画函数
const animateValue = (key, start, end, duration) => {
  if (start === end) return;
  const range = end - start;
  let current = start;
  const increment = end > start ? 1 : -1;
  const stepTime = Math.abs(Math.floor(duration / range));
  
  // 如果步长太小，就直接设置
  if (stepTime < 10 && range > 100) {
     const startTime = performance.now();
     const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out quartic
        const ease = 1 - Math.pow(1 - progress, 4);
        
        animatedStats[key] = start + (range * ease);
        
        if (progress < 1) {
           requestAnimationFrame(animate);
        } else {
           animatedStats[key] = end;
        }
     };
     requestAnimationFrame(animate);
  } else {
     // 简单定时器
     const timer = setInterval(() => {
        current += increment;
        animatedStats[key] = current;
        if (current === end) {
           clearInterval(timer);
        }
     }, Math.max(stepTime, 10)); // 最小10ms
  }
};

const updateStatsWithAnimation = (newData) => {
  const keys = ['total_users', 'new_users', 'active_users', 'answered_questions', 'accuracy', 'pending_corrections'];
  keys.forEach(key => {
    let targetValue = 0;
    if (key === 'new_users') targetValue = newData.summary_new_users || 0;
    else if (key === 'active_users') targetValue = newData.summary_active_users || 0;
    else if (key === 'answered_questions') targetValue = newData.summary_answered_questions || 0;
    else if (key === 'accuracy') targetValue = newData.summary_accuracy || 0;
    else if (key === 'pending_corrections') targetValue = newData.pending_corrections || 0;
    else targetValue = newData[key] || 0;
    
    // 如果是小数（如正确率），保留1位
    if (key === 'accuracy') {
       // 简单处理，不动画小数
       animatedStats[key] = targetValue;
    } else {
       animateValue(key, 0, targetValue, 1000);
    }
  });
};

const fetchDashboardData = async () => {
  loading.value = true;
  try {
    const [dashboardRes, correctionRes] = await Promise.all([
      getDashboardData(timeRange.value),
      getCorrectionStats()
    ]);

    if (dashboardRes.code === 0) {
      const data = dashboardRes.data || {};
      
      // 添加纠错数据
      if (correctionRes.code === 0 && correctionRes.data !== null && correctionRes.data !== undefined) {
        data.pending_corrections = typeof correctionRes.data === 'object' 
          ? (correctionRes.data.pending_count || correctionRes.data.pending || 0)
          : correctionRes.data;
      }

      // 触发数字动画
      updateStatsWithAnimation(data);
      
      notes.value = data.notes || '';
      
      // 更新列表
      recentUsers.value = data.recent_users || [];
      hotKnowledgePoints.value = data.hot_knowledge_points || [];

      // 更新图表数据
      if (Array.isArray(data.new_users)) {
        chartData.days = data.new_users.map(item => item.day);
        chartData.new_users = data.new_users.map(item => item.value);
        chartData.active_users = data.active_users?.map(item => item.value) || [];
        chartData.answered_questions = data.answered_questions?.map(item => item.value) || [];
        chartData.accuracy = data.accuracy?.map(item => item.value) || [];

        nextTick(() => {
          initChart();
        });
      }
    }
  } catch (error) {
    console.error(error);
    message.error('获取数据失败');
  } finally {
    loading.value = false;
  }
};

const handleTimeRangeChange = () => {
  fetchDashboardData();
};

const initChart = () => {
  if (!chartRef.value) return;
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      padding: [10, 15],
      textStyle: { color: '#333' },
      extraCssText: 'box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-radius: 8px;'
    },
    legend: {
      data: ['新增用户', '活跃用户', '已答题目', '正确率'],
      bottom: 0,
      icon: 'circle'
    },
    grid: {
      left: '2%',
      right: '2%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.days,
      axisLabel: {
        formatter: (value) => value.split('-').slice(1).join('-'),
        color: '#8c8c8c'
      },
      axisLine: { lineStyle: { color: '#f0f0f0' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '数量',
        position: 'left',
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLabel: { color: '#8c8c8c' }
      },
      {
        type: 'value',
        name: '正确率(%)',
        position: 'right',
        max: 100,
        splitLine: { show: false },
        axisLabel: { color: '#8c8c8c' }
      }
    ],
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: chartData.new_users,
        itemStyle: { color: '#1890ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24,144,255,0.2)' },
            { offset: 1, color: 'rgba(24,144,255,0)' }
          ])
        }
      },
      {
        name: '活跃用户',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: chartData.active_users,
        itemStyle: { color: '#52c41a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82,196,26,0.2)' },
            { offset: 1, color: 'rgba(82,196,26,0)' }
          ])
        }
      },
      {
        name: '已答题目',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: chartData.answered_questions,
        itemStyle: { color: '#722ed1' }
      },
      {
        name: '正确率',
        type: 'line',
        smooth: true,
        symbol: 'none',
        yAxisIndex: 1,
        data: chartData.accuracy,
        itemStyle: { color: '#faad14' },
        lineStyle: { type: 'dashed' }
      }
    ]
  };

  chartInstance.setOption(option);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatNumber = (num) => {
  if (typeof num !== 'number') return num;
  // 如果是小数，保留1位
  if (num % 1 !== 0) return num.toFixed(1);
  return num.toLocaleString();
};

const getAvatarColor = (index) => {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae'];
  return colors[index % colors.length];
};

const handleResize = () => {
  chartInstance && chartInstance.resize();
};

onMounted(() => {
  fetchDashboardData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
  }
});
</script>

<style scoped>
.dashboard-container {
  min-height: 100%;
  padding-bottom: 24px;
}

/* 动画定义 */
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-down {
  animation: slideDown 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.animate-fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

/* 欢迎区域 */
.welcome-section {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  padding: 32px 40px;
  border-radius: 12px;
  margin-bottom: 32px;
  color: #fff;
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.2);
  overflow: hidden;
}

.welcome-bg-decoration {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background-image: radial-gradient(circle at 90% 10%, rgba(255,255,255,0.1) 0%, transparent 20%),
                    radial-gradient(circle at 10% 90%, rgba(255,255,255,0.1) 0%, transparent 20%);
  pointer-events: none;
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 16px;
}

.last-login-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.15);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-weight: 500;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
}

/* 统计卡片网格 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card-wrapper {
  opacity: 0; /* for animation */
}

.stat-card {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

.stat-card-body {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  transition: all 0.3s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.total-bg { background: #e6f7ff; color: #1890ff; }
.new-bg { background: #fff0f6; color: #eb2f96; }
.active-bg { background: #f6ffed; color: #52c41a; }
.practice-bg { background: #f9f0ff; color: #722ed1; }
.accuracy-bg { background: #fffbe6; color: #faad14; }
.correction-bg { background: #fff1f0; color: #f5222d; }

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f1f1f;
  line-height: 1.2;
}

.stat-value .suffix {
  font-size: 14px;
  margin-left: 4px;
  color: #8c8c8c;
  font-weight: normal;
}

.stat-card-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  opacity: 0.1;
  pointer-events: none;
  transition: all 0.5s;
}

.stat-card:hover .stat-card-decoration {
  transform: scale(1.2);
  opacity: 0.15;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 32px;
}

.chart-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chart-note {
  color: #faad14;
  font-size: 13px;
  background: #fffbe6;
  padding: 4px 12px;
  border-radius: 4px;
}

.chart-container {
  height: 380px;
  width: 100%;
}

/* 列表区域 */
.list-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  height: 100%;
}

.user-list-item {
  padding: 16px 0;
  transition: all 0.3s;
}

.user-list-item:hover {
  background: #fafafa;
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 8px;
  margin: 0 -12px;
}

.list-item-title {
  font-weight: 600;
  color: #1f1f1f;
  font-size: 15px;
}

.list-item-desc {
  font-size: 13px;
  color: #8c8c8c;
}

.user-action-tag {
  font-size: 12px;
  color: #1890ff;
  background: #e6f7ff;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 排行榜 */
.rank-badge {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: #f0f0f0;
  border-radius: 6px;
  margin-right: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #8c8c8c;
  transition: all 0.3s;
}

.rank-1 { background-color: #ff4d4f; color: #fff; box-shadow: 0 2px 8px rgba(255, 77, 79, 0.4); }
.rank-2 { background-color: #ff7a45; color: #fff; box-shadow: 0 2px 8px rgba(255, 122, 69, 0.4); }
.rank-3 { background-color: #ffc53d; color: #fff; box-shadow: 0 2px 8px rgba(255, 197, 61, 0.4); }

.knowledge-item {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.knowledge-item:last-child {
  border-bottom: none;
}

.knowledge-content {
  width: 100%;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.error-rate-text {
  color: #ff4d4f;
  font-weight: 700;
  font-size: 16px;
}

.rate-label {
  font-size: 12px;
  font-weight: normal;
  color: #8c8c8c;
  margin-left: 2px;
}

.knowledge-progress-wrapper {
  margin-bottom: 12px;
  padding-right: 24px;
}

.knowledge-meta-row {
  font-size: 12px;
  color: #8c8c8c;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fafafa;
  padding: 6px 12px;
  border-radius: 4px;
  display: inline-flex;
}

.empty-content {
  display: flex;
  align-items: center;
  height: 60px;
  opacity: 0.5;
}

.empty-rank {
  background-color: #f5f5f5;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }
  
  .welcome-action {
    margin-top: 16px;
    width: 100%;
  }
  
  .refresh-btn {
    width: 100%;
  }
  
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
