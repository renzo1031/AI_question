<template>
  <a-layout style="height: 100vh; overflow: hidden">
    <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible theme="light" class="custom-sider">
      <div class="logo" :class="{ 'collapsed': collapsed }">
        <img src="../assets/logo.svg" alt="logo" />
        <span v-show="!collapsed">管理后台</span>
      </div>
      <div class="menu-container">
        <a-menu v-model:selectedKeys="selectedKeys" theme="light" mode="inline" @click="handleMenuClick">
          <a-menu-item key="/">
            <pie-chart-outlined />
            <span>首页</span>
          </a-menu-item>
          
          <a-menu-item key="/Workplace">
            <desktop-outlined />
            <span>工作台</span>
          </a-menu-item>
          
          <a-sub-menu key="sub2">
            <template #title>
              <span>
                <book-outlined />
                <span>教务管理</span>
              </span>
            </template>
            <a-menu-item key="/grade/list">
              <ordered-list-outlined />
              <span>年级列表</span>
            </a-menu-item>
            <a-menu-item key="/subject/list">
              <tags-outlined />
              <span>学科列表</span>
            </a-menu-item>
            <a-menu-item key="/subject/knowledge-points">
              <bulb-outlined />
              <span>知识点管理</span>
            </a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="sub_question">
            <template #title>
              <span>
                <a-badge :count="collapsed ? correctionCount : 0" :offset="[10, 7]" size="small" :overflow-count="99">
                  <read-outlined />
                </a-badge>
                <span v-if="!collapsed" style="margin-left: 10px">
                  <a-badge :count="!collapsed ? correctionCount : 0" :offset="[5, -3]" size="small" :overflow-count="99">
                    <span>题库中心</span>
                  </a-badge>
                </span>
              </span>
            </template>
            <a-menu-item key="/question/list">
              <database-outlined />
              <span>题库管理</span>
            </a-menu-item>
            <a-menu-item key="/question/correction">
              <solution-outlined />
              <a-badge :count="correctionCount" :offset="[7, -3]" size="small" :overflow-count="99">
                <span>纠错管理</span>
              </a-badge>
            </a-menu-item>
          </a-sub-menu>

          <a-sub-menu key="sub1">
            <template #title>
              <span>
                <user-outlined />
                <span>用户管理</span>
              </span>
            </template>
            <a-menu-item key="/user/list">
              <team-outlined />
              <span>用户列表</span>
            </a-menu-item>
          </a-sub-menu>

          <a-sub-menu key="sub_system">
            <template #title>
              <span>
                <setting-outlined />
                <span>系统管理</span>
              </span>
            </template>
            <a-menu-item key="/system/announcement">
              <sound-outlined />
              <span>公告管理</span>
            </a-menu-item>
            <a-menu-item key="/system/banner">
              <picture-outlined />
              <span>轮播图管理</span>
            </a-menu-item>
            <a-menu-item key="/system/config">
              <tool-outlined />
              <span>系统配置</span>
            </a-menu-item>
            <a-menu-item key="/system/log">
              <safety-outlined />
              <span>系统日志</span>
            </a-menu-item>
          </a-sub-menu>
        </a-menu>
      </div>
      
      <!-- 底部用户信息 -->
      <div class="sider-footer" :class="{ 'collapsed': collapsed }">
        <a-dropdown placement="top">
          <div class="user-info-trigger">
            <a-avatar :src="userInfo?.avatar || 'https://api.dicebear.com/7.x/miniavs/svg?seed=1'">
              <template #icon><UserOutlined /></template>
            </a-avatar>
            <div class="user-details" v-show="!collapsed">
              <div class="user-name">{{ userInfo?.name || '管理员' }}</div>
              <div class="user-role">超级管理员</div>
            </div>
            <LogoutOutlined v-show="!collapsed" class="logout-icon" />
          </div>
          <template #overlay>
            <a-menu>
              <a-menu-item @click="router.push('/profile')">
                <a href="javascript:;">个人中心</a>
              </a-menu-item>
              <a-menu-item @click="handleLogout">
                <a href="javascript:;">退出登录</a>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout-sider>
    <a-layout style="display: flex; flex-direction: column; overflow: hidden">
      <a-layout-header style="background: #fff; padding: 0 16px; display: flex; align-items: center; box-shadow: 0 1px 4px rgba(0,21,41,.08); position: relative; z-index: 1;">
        <!-- 折叠按钮 -->
        <component
          :is="collapsed ? MenuUnfoldOutlined : MenuFoldOutlined"
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />

        <!-- 面包屑 -->
        <a-breadcrumb style="margin-left: 16px; flex: 1;">
          <a-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
            <router-link :to="item.path" v-if="item.path">{{ item.meta.title }}</router-link>
            <span v-else>{{ item.meta.title }}</span>
          </a-breadcrumb-item>
        </a-breadcrumb>
      </a-layout-header>
      
      <!-- 多标签页 -->
      <div class="tabs-view">
        <a-tabs
          v-model:activeKey="activeTabKey"
          type="editable-card"
          hide-add
          @edit="onEdit"
          @change="onTabChange"
          class="custom-tabs"
        >
          <a-tab-pane
            v-for="pane in tabsList"
            :key="pane.path"
            :tab="pane.title"
            :closable="pane.path !== '/'"
          >
          </a-tab-pane>
        </a-tabs>
      </div>

      <div style="flex: 1; overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column;">
        <a-layout-content style="margin: 0 16px 16px; flex: none">
          <div :style="{ padding: '24px', background: '#fff', minHeight: '360px', borderRadius: '8px' }">
            <router-view v-slot="{ Component }">
              <keep-alive>
                <component :is="Component" />
              </keep-alive>
            </router-view>
          </div>
        </a-layout-content>
        <a-layout-footer style="text-align: center; margin-top: auto;">
          Ant Design Vue ©2025 Created by RenZhong
        </a-layout-footer>
      </div>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import {
  PieChartOutlined,
  DesktopOutlined,
  UserOutlined,
  BookOutlined,
  ReadOutlined,
  FileTextOutlined,
  SettingOutlined,
  SoundOutlined,
  ToolOutlined,
  SafetyOutlined,
  PictureOutlined,
  DownOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  LogoutOutlined,
  TeamOutlined,
  OrderedListOutlined,
  TagsOutlined,
  BulbOutlined,
  DatabaseOutlined,
  SolutionOutlined
} from '@ant-design/icons-vue';
import { useUserStore } from '../stores/user';
import { useTabsStore } from '../stores/tabs';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import { getCorrectionStats } from '../api/correction';

const collapsed = ref(false);
const selectedKeys = ref(['/']);
const correctionCount = ref(0);

const userStore = useUserStore();
const tabsStore = useTabsStore();
const router = useRouter();
const route = useRoute();

const userInfo = computed(() => userStore.userInfo);
const tabsList = computed(() => tabsStore.tabsList);
const activeTabKey = computed({
  get: () => tabsStore.activeKey,
  set: (val) => tabsStore.setActiveTab(val)
});

// 面包屑数据
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title);
  
  // 始终在最前面加上首页（如果当前不是首页）
  const first = matched[0];
  if (first && first.path !== '/' && first.path !== '') {
    return [{ path: '/', meta: { title: '首页' } }, ...matched];
  }
  
  return matched;
});

// 监听路由变化，添加标签页
watch(
  () => route.path,
  () => {
    selectedKeys.value = [route.path];
    tabsStore.addTab(route);
  },
  { immediate: true }
);

// 菜单点击
const handleMenuClick = ({ key }) => {
  router.push(key);
};

// 标签页切换
const onTabChange = (key) => {
  router.push(key);
};

// 标签页关闭
const onEdit = (targetKey, action) => {
  if (action === 'remove') {
    tabsStore.removeTab(targetKey);
  }
};

const handleLogout = async () => {
  const res = await userStore.logout();
  if (res && res.message) {
    message.success(res.message);
  } else {
    message.success('已退出登录');
  }
  router.push('/login');
};

const fetchCorrectionCount = async () => {
  try {
    const res = await getCorrectionStats();
    if (res.code === 0) {
      correctionCount.value = typeof res.data === 'object' 
        ? (res.data.pending_count || res.data.pending || 0)
        : res.data;
    }
  } catch (error) {
    console.error('Failed to fetch correction stats:', error);
  }
};

onMounted(() => {
  fetchCorrectionCount();
});
</script>

<style scoped>
.logo {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  white-space: nowrap;
  transition: all 0.3s;
  border-bottom: 1px solid #f0f0f0;
}

.logo img {
  height: 32px;
  width: 32px;
}

.logo span {
  margin-left: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #001529;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  opacity: 1;
  transition: opacity 0.3s;
}

.logo.collapsed {
  padding: 0;
}

.tabs-view {
  padding: 6px 16px 0;
  background: #f0f2f5;
}

.custom-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 0;
}

.custom-tabs :deep(.ant-tabs-content-holder) {
  display: none;
}

.trigger {
  font-size: 18px;
  line-height: 64px;
  padding: 0 24px 0 8px;
  cursor: pointer;
  transition: color 0.3s;
}
.trigger:hover {
  color: #1890ff;
}

.logo {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  white-space: nowrap;
  transition: all 0.3s;
}

.custom-sider {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.custom-sider :deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.sider-footer {
  padding: 16px;
  /* border-top: 1px solid #f0f0f0; */
}

.sider-footer.collapsed {
  padding: 16px 0;
  display: flex;
  justify-content: center;
}

.user-info-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
  overflow: hidden;
  white-space: nowrap;
}

.user-info-trigger:hover {
  background-color: rgba(0, 0, 0, 0.025);
}

.user-details {
  margin-left: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.logout-icon {
  margin-left: auto;
  color: #8c8c8c;
  font-size: 16px;
  transition: color 0.3s;
}

.user-info-trigger:hover .logout-icon {
  color: #ff4d4f;
}
</style>
