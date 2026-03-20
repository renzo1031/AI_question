<template>
  <div class="workplace-container">
    <a-row :gutter="[16, 16]">
      <!-- 左上角：日历 -->
      <a-col :span="24" :lg="12">
        <a-card title="日历视图" :bordered="false" class="h-full">
          <div class="calendar-wrapper">
            <a-calendar v-model:value="selectedDate" :fullscreen="false" @select="onDateSelect">
              <template #dateCellRender="{ current }">
                <div v-if="hasTaskOnDate(current)" class="calendar-dot"></div>
              </template>
            </a-calendar>
          </div>
        </a-card>
      </a-col>

      <!-- 右上角：待办事项 -->
      <a-col :span="24" :lg="12">
        <a-card title="待办事项" :bordered="false" class="h-full todo-card">
          <template #extra>
            <a-button type="primary" size="small" @click="showAddModal">
              <template #icon><PlusOutlined /></template>
              新增任务
            </a-button>
          </template>
          
          <div class="todo-list-container">
            <div class="current-date-label">{{ selectedDateStr }}</div>
            
            <a-empty v-if="filteredTasks.length === 0" description="暂无任务" />
            
            <a-list v-else item-layout="horizontal" :data-source="filteredTasks">
              <template #renderItem="{ item }">
                <a-list-item>
                  <template #actions>
                    <a-button type="text" danger size="small" @click="deleteTask(item.id)">
                      <DeleteOutlined />
                    </a-button>
                  </template>
                  <a-list-item-meta>
                    <template #title>
                      <a-checkbox v-model:checked="item.completed" @change="saveTasks">
                        <span :class="{ 'task-completed': item.completed }">{{ item.content }}</span>
                      </a-checkbox>
                    </template>
                    <template #description>
                      <span class="task-time">
                        {{ formatDate(item.startTime) }} - {{ formatDate(item.endTime) }}
                      </span>
                      <a-tag :color="getPriorityColor(item.priority)" size="small" class="ml-2">
                        {{ item.priority }}
                      </a-tag>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </div>
        </a-card>
      </a-col>

      <!-- 下方：甘特图 -->
      <a-col :span="24">
        <a-card title="任务甘特图" :bordered="false">
          <div ref="ganttChartRef" style="height: 400px; width: 100%"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 新增任务弹窗 -->
    <a-modal
      v-model:open="addModalVisible"
      title="新增任务"
      @ok="handleAddTask"
      destroyOnClose
    >
      <a-form :model="newTask" layout="vertical">
        <a-form-item label="任务内容" required>
          <a-input v-model:value="newTask.content" placeholder="请输入任务内容" />
        </a-form-item>
        <a-form-item label="时间范围" required>
          <a-range-picker 
            v-model:value="newTask.dateRange" 
            style="width: 100%" 
            :allowClear="false"
          />
        </a-form-item>
        <a-form-item label="优先级">
          <a-select v-model:value="newTask.priority">
            <a-select-option value="High">高</a-select-option>
            <a-select-option value="Medium">中</a-select-option>
            <a-select-option value="Low">低</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import isBetween from 'dayjs/plugin/isBetween';
import * as echarts from 'echarts';
import { message } from 'ant-design-vue';

dayjs.extend(isBetween);

// --- 状态定义 ---
const selectedDate = ref(dayjs());
const tasks = ref([]);
const addModalVisible = ref(false);
const ganttChartRef = ref(null);
let chartInstance = null;

const newTask = reactive({
  content: '',
  dateRange: [dayjs(), dayjs().add(1, 'day')],
  priority: 'Medium'
});

// --- 计算属性 ---
const selectedDateStr = computed(() => selectedDate.value.format('YYYY-MM-DD'));

// 筛选当前选中日期的任务（只要任务的时间段覆盖了选中日期）
const filteredTasks = computed(() => {
  const target = selectedDate.value;
  return tasks.value.filter(task => {
    const start = dayjs(task.startTime).startOf('day');
    const end = dayjs(task.endTime).endOf('day');
    return target.isBetween(start, end, 'day', '[]');
  });
});

// --- 方法 ---

// 初始化加载数据
onMounted(() => {
  loadTasks();
  initGanttChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
  }
});

const handleResize = () => {
  chartInstance && chartInstance.resize();
};

// 从 LocalStorage 加载
const loadTasks = () => {
  const saved = localStorage.getItem('workplace_tasks');
  if (saved) {
    try {
      tasks.value = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse tasks', e);
      tasks.value = [];
    }
  } else {
    // 默认初始数据
    tasks.value = [
      {
        id: Date.now(),
        content: '初始化项目结构',
        startTime: dayjs().subtract(2, 'day').valueOf(),
        endTime: dayjs().add(1, 'day').valueOf(),
        priority: 'High',
        completed: false
      }
    ];
    saveTasks();
  }
  updateGanttChart();
};

// 保存到 LocalStorage
const saveTasks = () => {
  localStorage.setItem('workplace_tasks', JSON.stringify(tasks.value));
  updateGanttChart();
};

// 日历选择
const onDateSelect = (date) => {
  selectedDate.value = date;
};

// 判断某天是否有任务
const hasTaskOnDate = (date) => {
  return tasks.value.some(task => {
    const start = dayjs(task.startTime).startOf('day');
    const end = dayjs(task.endTime).endOf('day');
    return date.isBetween(start, end, 'day', '[]');
  });
};

// 格式化日期显示
const formatDate = (timestamp) => {
  return dayjs(timestamp).format('MM-DD');
};

const getPriorityColor = (p) => {
  const map = { High: 'red', Medium: 'orange', Low: 'blue' };
  return map[p] || 'default';
};

// --- 模态框操作 ---
const showAddModal = () => {
  newTask.content = '';
  newTask.dateRange = [dayjs(), dayjs().add(1, 'day')];
  newTask.priority = 'Medium';
  addModalVisible.value = true;
};

const handleAddTask = () => {
  if (!newTask.content) {
    message.warning('请输入任务内容');
    return;
  }
  
  const task = {
    id: Date.now(),
    content: newTask.content,
    startTime: newTask.dateRange[0].valueOf(),
    endTime: newTask.dateRange[1].valueOf(),
    priority: newTask.priority,
    completed: false
  };
  
  tasks.value.push(task);
  saveTasks();
  addModalVisible.value = false;
  message.success('任务已添加');
};

const deleteTask = (id) => {
  tasks.value = tasks.value.filter(t => t.id !== id);
  saveTasks();
  message.success('任务已删除');
};

// --- 甘特图实现 ---
const initGanttChart = () => {
  if (!ganttChartRef.value) return;
  chartInstance = echarts.init(ganttChartRef.value);
  updateGanttChart();
};

const updateGanttChart = () => {
  if (!chartInstance) return;

  // 准备数据
  // ECharts 甘特图通常使用 Bar Chart Stack
  // 按照开始时间排序任务，以便展示更直观
  const sortedTasks = [...tasks.value].sort((a, b) => a.startTime - b.startTime);
  
  const categories = sortedTasks.map(t => t.content);
  const startTimes = sortedTasks.map(t => t.startTime);
  const durations = sortedTasks.map(t => t.endTime - t.startTime);

  // 转换时间戳为基准时间差，或者直接使用 time axis (更复杂)，这里用简单的 stack bar
  // 为了让 ECharts 正确显示时间轴，最好使用 Custom Series 或者 renderItem，
  // 但为了简化，我们使用 stack bar，第一段是透明的（offset），第二段是实际长度。
  
  // 计算相对于最早任务的时间偏移
  const minTime = Math.min(...startTimes);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function (params) {
        const taskName = params[1].name;
        const taskIndex = categories.indexOf(taskName);
        if (taskIndex === -1) return '';
        const task = sortedTasks[taskIndex];
        return `${taskName}<br/>开始: ${dayjs(task.startTime).format('YYYY-MM-DD')}<br/>结束: ${dayjs(task.endTime).format('YYYY-MM-DD')}<br/>状态: ${task.completed ? '已完成' : '进行中'}`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value) => dayjs(value).format('MM-DD')
      }
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true // 让第一个任务在最上面
    },
    series: [
      {
        name: 'Placeholder',
        type: 'bar',
        stack: 'Total',
        itemStyle: {
          borderColor: 'transparent',
          color: 'transparent'
        },
        emphasis: {
          itemStyle: {
            borderColor: 'transparent',
            color: 'transparent'
          }
        },
        data: startTimes
      },
      {
        name: 'Task Duration',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'inside',
          formatter: (params) => {
             const index = params.dataIndex;
             return sortedTasks[index].completed ? '√' : '';
          }
        },
        itemStyle: {
           color: (params) => {
             const index = params.dataIndex;
             const task = sortedTasks[index];
             return task.completed ? '#52c41a' : '#1890ff';
           },
           borderRadius: 4
        },
        data: sortedTasks.map(t => t.endTime)
      }
    ]
  };
  
  // 注意：上面的 stack bar + time axis 组合在 ECharts 中处理时间戳稍微有点特殊
  // 标准的做法是：series 1 data 是 start time，series 2 data 是 end time
  // 但是 stack bar 的逻辑是累加。所以 series 2 应该是 duration。
  // 可是 xAxis type='time' 时，value 应该是绝对时间戳。
  // 所以 stack bar 配合 time axis 比较 tricky。
  // 更稳妥的方法是使用 Custom Series (renderItem)。
  
  // 让我们改用 Custom Series 来渲染甘特图，这样最灵活且准确
  
  const customOption = {
    tooltip: {
      formatter: (params) => {
        const task = sortedTasks[params.dataIndex];
        return `${task.content}<br/>
                开始: ${dayjs(task.startTime).format('YYYY-MM-DD')}<br/>
                结束: ${dayjs(task.endTime).format('YYYY-MM-DD')}<br/>
                状态: ${task.completed ? '已完成' : '进行中'}`;
      }
    },
    grid: {
      left: '10%',
      right: '4%',
      bottom: '10%'
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value) => dayjs(value).format('MM-DD')
      }
    },
    yAxis: {
      data: categories,
      inverse: true
    },
    series: [
      {
        type: 'custom',
        renderItem: function (params, api) {
          const categoryIndex = api.value(0);
          const start = api.coord([api.value(1), categoryIndex]);
          const end = api.coord([api.value(2), categoryIndex]);
          const height = api.size([0, 1])[1] * 0.6;
          
          const rectShape = echarts.graphic.clipRectByRect(
            {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height
            },
            {
              x: params.coordSys.x,
              y: params.coordSys.y,
              width: params.coordSys.width,
              height: params.coordSys.height
            }
          );
          
          return (
            rectShape && {
              type: 'rect',
              transition: ['shape'],
              shape: rectShape,
              style: api.style()
            }
          );
        },
        itemStyle: {
          opacity: 0.8,
          color: (params) => {
             return sortedTasks[params.dataIndex].completed ? '#52c41a' : '#1890ff';
          }
        },
        encode: {
          x: [1, 2],
          y: 0
        },
        data: sortedTasks.map((task, index) => {
           return [index, task.startTime, task.endTime, task.completed];
        })
      }
    ]
  };

  chartInstance.setOption(customOption);
};

// 监听 selectedDate 变化来更新甘特图高亮（可选，目前不做高亮，只做全览）
</script>

<style scoped>
.workplace-container {
  padding: 0;
  margin: -24px;
  margin-top: -12px;
  overflow-x: hidden;
  padding: 24px;
}

.calendar-wrapper {
  border: 1px solid #f0f0f0;
  border-radius: 2px;
}

.calendar-dot {
  width: 6px;
  height: 6px;
  background: #1890ff;
  border-radius: 50%;
  margin: 0 auto;
  margin-top: 4px;
}

.todo-card {
  display: flex;
  flex-direction: column;
}

.todo-list-container {
  flex: 1;
  overflow-y: auto;
  max-height: 400px; /* 限制高度，避免过长 */
}

.current-date-label {
  font-weight: bold;
  margin-bottom: 12px;
  color: #1890ff;
}

.task-completed {
  text-decoration: line-through;
  color: #999;
}

.task-time {
  font-size: 12px;
  color: #999;
}

.ml-2 {
  margin-left: 8px;
}

.h-full {
  height: 100%;
}
</style>