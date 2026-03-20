# AI 题库后台管理系统 (前端)

基于 Vue 3 + Vite + Ant Design Vue 开发的题库后台管理系统前端项目。

## 🛠 技术栈

- **核心框架**: [Vue 3](https://cn.vuejs.org/) (Script Setup)
- **构建工具**: [Vite](https://cn.vitejs.dev/)
- **UI 组件库**: [Ant Design Vue 4](https://next.antdv.com/components/overview-cn)
- **状态管理**: [Pinia](https://pinia.vuejs.org/zh/)
- **路由管理**: [Vue Router 4](https://router.vuejs.org/zh/)
- **HTTP 客户端**: [Axios](https://axios-http.com/)
- **图表库**: [ECharts](https://echarts.apache.org/zh/index.html)
- **模拟数据**: [Mock.js](http://mockjs.com/)

## ✨ 功能特性

### 📊 工作台 (Workplace)
- **待办日历**: 左侧日历视图，直观展示每日待办事项状态。
- **待办事项管理**: 右侧待办列表，支持添加、删除、优先级标记（高/中/低），数据通过 LocalStorage 持久化。
- **项目进度**: 底部甘特图 (Gantt Chart)，可视化展示任务的时间跨度和进度。
- **系统公告**: 展示系统发布的最新公告信息。

### 👥 用户管理
- **用户列表**: 用户信息的增删改查，支持头像展示（集成 Dicebear Avatar API）。
- **个人中心**: 用户个人资料查看与编辑。
- **登录/注册**: 完整的用户认证流程。

### 📚 题库管理
- **题目列表**: 题目的管理与查询，支持按年级颜色区分显示。
- **学科管理**: 题库学科分类管理。
- **知识点管理**: 知识点体系建设。
- **年级管理**: 年级分类设置。

### ⚙️ 系统管理
- **系统配置**: 平台基础参数配置。
- **系统日志**: 操作日志记录与查询。
- **公告管理**: 系统公告发布与维护。
- **批改管理**: 智能批改记录查看。

## 🚀 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 构建生产环境

```bash
npm run build
```

## 📂 目录结构

```
src/
├── api/          # API 接口封装
├── assets/       # 静态资源 (图片, 样式等)
├── mock/         # Mock 数据模拟
├── router/       # 路由配置
├── stores/       # Pinia 状态管理
├── utils/        # 工具函数 (请求封装等)
├── views/        # 页面组件
│   ├── Workplace.vue   # 工作台 (核心功能页)
│   ├── ...
├── App.vue       # 根组件
└── main.js       # 入口文件
```

## 📝 最近更新

- **Workplace 重构**: 全新的三栏布局（日历/待办/甘特图），移除冗余装饰组件。
- **UI 优化**: 修复了 Modal 组件警告 (`visible` -> `open`)，优化了年级标签的视觉显示。
- **稳定性修复**: 修复了头像图片加载失败的问题，替换为更稳定的 Avatar 服务。
