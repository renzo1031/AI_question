<template>
  <div class="user-list-container">
    <a-card :bordered="false" class="search-card">
      <a-form layout="inline" :model="searchParams" @finish="handleSearch">
        <a-form-item label="关键词">
          <a-input v-model:value="searchParams.keyword" placeholder="邮箱/手机号/昵称" allow-clear />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchParams.status" placeholder="全部" style="width: 120px" allow-clear>
            <a-select-option value="active">启用</a-select-option>
            <a-select-option value="disabled">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="用户列表" :bordered="false" style="margin-top: 24px">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="pagination"
        :loading="loading"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'userInfo'">
            <div style="display: flex; align-items: center;">
              <a-avatar :src="record.avatar || 'https://api.dicebear.com/7.x/miniavs/svg?seed=1'" />
              <div style="margin-left: 12px;">
                <div style="font-weight: 500;">{{ record.nickname || '未设置昵称' }}</div>
                <div style="color: #999; font-size: 12px;">{{ record.email }}</div>
              </div>
            </div>
          </template>
          
          <template v-else-if="column.dataIndex === 'status'">
            <a-badge status="success" text="启用" v-if="record.status === 'active'" />
            <a-badge status="error" text="禁用" v-else />
          </template>
          
          <template v-else-if="column.dataIndex === 'created_at'">
            {{ new Date(record.created_at).toLocaleString() }}
          </template>
          
          <template v-else-if="column.dataIndex === 'action'">
            <a @click="showDetail(record)">详情</a>
            <a-divider type="vertical" />
            <a-popconfirm 
              v-if="record.status === 'active'"
              title="确定禁用该用户吗？" 
              @confirm="handleStatusChange(record, 'disabled')"
            >
              <a style="color: red">禁用</a>
            </a-popconfirm>
            <a-popconfirm 
              v-else
              title="确定启用该用户吗？" 
              @confirm="handleStatusChange(record, 'active')"
            >
              <a style="color: green">启用</a>
            </a-popconfirm>
            <a-divider type="vertical" />
            <a-dropdown>
              <a class="ant-dropdown-link" @click.prevent>
                更多 <DownOutlined />
              </a>
              <template #overlay>
                <a-menu>
                  <a-menu-item>
                    <a @click="showPasswordModal(record)">重置密码</a>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Password Modal -->
    <a-modal v-model:open="passwordModalVisible" title="重置密码" @ok="handlePasswordOk" :confirmLoading="actionLoading">
      <p>当前用户: {{ currentUser?.nickname }}</p>
      <a-form-item label="新密码">
        <a-input-password v-model:value="newPassword" />
      </a-form-item>
    </a-modal>

    <!-- Detail Drawer -->
    <a-drawer
      v-model:open="detailVisible"
      title="用户详情"
      width="600"
    >
      <div v-if="userDetail">
        <div class="user-profile-header">
          <a-avatar :size="80" :src="userDetail.avatar || 'https://api.dicebear.com/7.x/miniavs/svg?seed=1'" />
          <div class="user-profile-info">
            <div class="user-profile-name">
              {{ userDetail.nickname || '未设置昵称' }}
              <a-tag :color="userDetail.status === 'active' ? 'success' : 'error'" class="status-tag">
                {{ userDetail.status === 'active' ? '启用' : '禁用' }}
              </a-tag>
            </div>
            <div class="user-profile-id">ID: {{ userDetail.id }}</div>
          </div>
        </div>

        <a-divider />

        <a-descriptions title="详细信息" bordered :column="1">
          <a-descriptions-item label="邮箱">{{ userDetail.email }}</a-descriptions-item>
          <a-descriptions-item label="手机">{{ userDetail.phone || '-' }}</a-descriptions-item>
          <a-descriptions-item label="性别">{{ formatGender(userDetail.gender) }}</a-descriptions-item>
          <a-descriptions-item label="生日">{{ formatDate(userDetail.birthday) }}</a-descriptions-item>
          <a-descriptions-item label="注册时间">{{ formatDate(userDetail.created_at) }}</a-descriptions-item>
          <a-descriptions-item label="上次登录">{{ formatDate(userDetail.last_login_at) }}</a-descriptions-item>
        </a-descriptions>
        
        <a-descriptions title="禁用信息" bordered :column="1" style="margin-top: 24px" v-if="userDetail.status !== 'active' && userDetail.disabled_at">
          <a-descriptions-item label="禁用时间">{{ formatDate(userDetail.disabled_at) }}</a-descriptions-item>
          <a-descriptions-item label="禁用原因">{{ userDetail.disabled_reason || '-' }}</a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { DownOutlined } from '@ant-design/icons-vue';
import { getUserList, updateUserStatus, resetUserPassword, getUserDetail } from '../api/user';

const loading = ref(false);
const dataSource = ref([]);
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
});

const searchParams = reactive({
  keyword: '',
  status: undefined,
});

const columns = [
  {
    title: '用户信息',
    dataIndex: 'userInfo',
    key: 'userInfo',
  },
  {
    title: '手机号',
    dataIndex: 'phone',
    key: 'phone',
    customRender: ({ text }) => text || '-',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '注册时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 200,
  },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchParams,
    };
    
    // Filter undefined or empty strings
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    const res = await getUserList(params);
    if (res.code === 0) {
      dataSource.value = res.data || [];
      pagination.total = res.page_info?.total || 0;
    }
  } catch (error) {
    console.error(error);
    message.error('获取用户列表失败');
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
  searchParams.status = undefined;
  handleSearch();
};

// Status Change
const handleStatusChange = async (record, status) => {
  try {
    await updateUserStatus(record.id, status);
    message.success('状态更新成功');
    fetchData();
  } catch (e) {
    console.error(e);
    message.error('状态更新失败');
  }
};

// Password Modal
const passwordModalVisible = ref(false);
const currentUser = ref(null);
const actionLoading = ref(false);
const newPassword = ref('');

const showPasswordModal = (record) => {
  currentUser.value = record;
  newPassword.value = '';
  passwordModalVisible.value = true;
};

const handlePasswordOk = async () => {
  if (!currentUser.value || !newPassword.value) {
    message.warning('请输入新密码');
    return;
  }
  actionLoading.value = true;
  try {
    await resetUserPassword(currentUser.value.id, newPassword.value);
    message.success('密码重置成功');
    passwordModalVisible.value = false;
  } catch (e) {
    console.error(e);
    message.error('重置密码失败');
  } finally {
    actionLoading.value = false;
  }
};

// Detail Drawer
const detailVisible = ref(false);
const userDetail = ref(null);

const showDetail = async (record) => {
  try {
    const res = await getUserDetail(record.id);
    if (res.code === 0) {
      userDetail.value = res.data;
      detailVisible.value = true;
    }
  } catch (e) {
    console.error(e);
    message.error('获取详情失败');
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

const formatGender = (gender) => {
  const map = {
    male: '男',
    female: '女',
    unknown: '未知'
  };
  return map[gender] || gender || '-';
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.user-list-container {
  min-height: 100%;
}

.user-profile-header {
  display: flex;
  align-items: center;
  padding: 0 12px;
}

.user-profile-info {
  margin-left: 24px;
}

.user-profile-name {
  font-size: 20px;
  font-weight: 600;
  color: #1f1f1f;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.user-profile-id {
  color: #8c8c8c;
  font-size: 14px;
}

.status-tag {
  margin-left: 12px;
}
</style>
