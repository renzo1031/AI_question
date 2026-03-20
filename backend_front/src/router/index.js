import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Home, // Home 是 Layout 容器
      meta: { requiresAuth: true },
      children: [
        {
          path: '', // 默认子路由
          name: 'dashboard',
          component: () => import('../views/Dashboard.vue'),
          meta: { title: '首页' }
        },
        {
          path: 'Workplace',
          name: 'workplace',
          component: () => import('../views/Workplace.vue'),
          meta: { title: '工作台' }
        },
        {
          path: 'user/list',
          name: 'user-list',
          component: () => import('../views/UserList.vue'),
          meta: { title: '用户列表' }
        },
        {
          path: 'grade/list',
          name: 'grade-list',
          component: () => import('../views/GradeList.vue'),
          meta: { title: '年级管理' }
        },
        {
          path: 'subject/list',
          name: 'subject-list',
          component: () => import('../views/SubjectList.vue'),
          meta: { title: '学科管理' }
        },
        {
          path: 'subject/knowledge-points',
          name: 'knowledge-points',
          component: () => import('../views/KnowledgePoints.vue'),
          meta: { title: '知识点管理' }
        },
        {
          path: 'question/list',
          name: 'question-list',
          component: () => import('../views/QuestionList.vue'),
          meta: { title: '题库管理' }
        },
        {
          path: 'question/correction',
          name: 'question-correction',
          component: () => import('../views/CorrectionList.vue'),
          meta: { title: '纠错管理' }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/Profile.vue'),
          meta: { title: '个人中心' }
        },
        {
          path: 'system/log',
          name: 'system-log',
          component: () => import('../views/SystemLog.vue'),
          meta: { title: '系统日志' }
        },
        {
          path: 'system/announcement',
          name: 'announcement-list',
          component: () => import('../views/AnnouncementList.vue'),
          meta: { title: '公告管理' }
        },
        {
          path: 'system/config',
          name: 'system-config',
          component: () => import('../views/SystemConfig.vue'),
          meta: { title: '系统配置' }
        },
        {
          path: 'system/banner',
          name: 'banner-list',
          component: () => import('../views/BannerList.vue'),
          meta: { title: '轮播图管理' }
        }
      ]
    },
    {
      path: '/login',
    name: 'login',
      component: Login,
      meta: { title: '登录' }
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { title: '注册' }
    }
  ]
});

// 简单的路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
