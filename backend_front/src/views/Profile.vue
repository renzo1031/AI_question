<template>
  <div class="profile-container">
    <a-row :gutter="24">
      <a-col :span="8">
        <a-card :bordered="false" class="profile-card">
          <div class="profile-header">
            <a-avatar :size="100" :src="userInfo?.avatar || 'https://api.dicebear.com/7.x/miniavs/svg?seed=1'" />
            <h2 class="nickname">{{ userInfo?.name || '管理员' }}</h2>
            <p class="role-tag"><a-tag color="blue">管理员</a-tag></p>
          </div>
          <a-divider />
          <div class="profile-info">
            <p><UserOutlined /> 邮箱：{{ userInfo?.email }}</p>
            <p><PhoneOutlined /> 手机：{{ userInfo?.phone || '未绑定' }}</p>
            <p><CalendarOutlined /> 注册时间：{{ formatDate(userInfo?.created_at) }}</p>
          </div>
        </a-card>
      </a-col>
      
      <a-col :span="16">
        <a-card title="基本资料" :bordered="false">
          <a-form
            :model="formState"
            layout="vertical"
            @finish="onFinish"
          >
            <a-form-item label="姓名" name="name" :rules="[{ required: true, message: '请输入姓名' }]">
              <a-input v-model:value="formState.name" />
            </a-form-item>

            <a-form-item
              label="邮箱"
              name="email"
              :rules="[{ type: 'email', message: '请输入有效的邮箱地址' }]"
            >
              <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
            </a-form-item>

            <a-form-item
              label="手机号"
              name="phone"
              :rules="[{ pattern: /^1\d{10}$/, message: '请输入有效的11位手机号' }]"
            >
              <a-input v-model:value="formState.phone" placeholder="请输入手机号" />
            </a-form-item>
            
            <a-form-item label="年级" name="grade">
              <a-select v-model:value="formState.grade" placeholder="请选择年级">
                <a-select-option value="1年级">1年级</a-select-option>
                <a-select-option value="2年级">2年级</a-select-option>
                <a-select-option value="3年级">3年级</a-select-option>
                <a-select-option value="4年级">4年级</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="头像URL" name="avatar">
              <a-input v-model:value="formState.avatar" placeholder="请输入头像图片地址" />
            </a-form-item>

            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="loading">保存修改</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useUserStore } from '../stores/user';
import { message } from 'ant-design-vue';
import { UserOutlined, PhoneOutlined, CalendarOutlined } from '@ant-design/icons-vue';

const userStore = useUserStore();
const loading = ref(false);
const userInfo = computed(() => userStore.userInfo);

const formState = reactive({
  name: '',
  grade: undefined,
  avatar: '',
  email: '',
  phone: ''
});

// 初始化表单数据
const initForm = () => {
  if (userInfo.value) {
    formState.name = userInfo.value.name;
    formState.grade = userInfo.value.grade;
    formState.avatar = userInfo.value.avatar;
    formState.email = userInfo.value.email;
    formState.phone = userInfo.value.phone;
  }
};

watch(() => userInfo.value, () => {
  initForm();
}, { immediate: true });

onMounted(async () => {
  try {
    await userStore.getUserInfo();
  } catch (error) {
    console.error(error);
  }
});

const onFinish = async (values) => {
  loading.value = true;
  try {
    // 处理空字符串为 null，避免后端正则验证失败
    const payload = { ...values };
    if (!payload.phone) payload.phone = null;
    if (!payload.email) payload.email = null;
    if (!payload.avatar) payload.avatar = null;

    await userStore.updateUserInfo(payload);
    message.success('更新成功');
  } catch (error) {
    message.error(error.message || '更新失败');
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString();
};
</script>

<style scoped>
.profile-card {
  text-align: center;
}
.profile-header {
  margin-bottom: 24px;
}
.nickname {
  margin: 16px 0 8px;
  font-size: 24px;
  font-weight: 500;
  color: #333;
}
.profile-info p {
  text-align: left;
  margin-bottom: 12px;
  color: #666;
  font-size: 14px;
}
.profile-info .anticon {
  margin-right: 8px;
  color: #1890ff;
}
</style>
