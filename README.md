# AI_question

一个围绕“AI 解题 + 学习闭环”设计的智能学习系统仓库，当前由后端服务、后台管理端、微信小程序端三部分组成。项目目标不是只做一次性搜题，而是把拍照搜题、题库管理、练习、错题沉淀、学习分析和运营配置串成完整链路。

## 项目概览

本仓库包含 3 个独立工程：

| 目录 | 角色 | 说明 |
| --- | --- | --- |
| `backend` | 后端服务 | 基于 FastAPI 的统一 API 服务，负责认证、题库、AI 解题、学习数据、后台管理能力 |
| `backend_front` | 后台管理端 | 基于 Vue 3 + Vite + Ant Design Vue 的管理系统，用于运营、题库和系统配置管理 |
| `front` | 微信小程序端 | 面向学生用户的学习端，提供搜题、练习、错题本、学习分析、个人中心等功能 |

## 系统关系

```text
  微信小程序   front ─────┐
                        ├──> backend (FastAPI + PostgreSQL + Redis + MinIO + AI/OCR)
后台管理端 backend_front ─┘
```

- `backend` 提供统一接口，接口前缀为 `/api/v1`
- `backend_front` 默认通过 Vite 代理访问 `http://localhost:8000`
- `front` 默认在 `front/utils/config.js` 中直连 `http://localhost:8000/api/v1`

## 核心能力

### 1. 学生端能力

- AI 文本解题、图片解题、拍照搜题
- AI 聊天、搜索结果、历史记录
- 练习刷题与答题页面
- 错题本与错题详情
- 学习分析与进度展示
- 个人中心、登录注册、资料编辑

### 2. 后台管理能力

- 管理员登录注册、权限与会话管理
- 工作台/仪表盘统计
- 用户管理
- 年级、学科、知识点管理
- 题库管理与批改/纠错管理
- 公告管理、轮播图管理
- 系统配置、系统日志

### 3. 后端支撑能力

- JWT + Session 双认证体系
- PostgreSQL 异步数据访问
- Redis 缓存与状态管理
- Alembic 数据库迁移
- MinIO 对象存储
- 阿里云 OCR 识题
- 多模型接入：通义、DeepSeek、Kimi、OpenAI 兼容服务
- 后台任务、统一日志、统一异常响应

## 技术栈

### 后端 `backend`

- FastAPI
- SQLAlchemy 2.0 + asyncpg
- PostgreSQL
- Redis
- Alembic
- MinIO
- Loguru
- DashScope / DeepSeek / Kimi / OpenAI-compatible API

### 后台管理端 `backend_front`

- Vue 3
- Vite
- Ant Design Vue
- Pinia
- Vue Router
- Axios
- ECharts
- vue-cropper

### 微信小程序端 `front`

- 微信小程序原生开发
- WXML / WXSS / JavaScript
- Glass Easel 组件框架

## 目录结构

```text
AI_question/
├── backend/         # FastAPI 后端
├── backend_front/   # Vue 管理后台
└── front/           # 微信小程序
```

各子项目内部都有自己的 README 和更细分的目录说明，建议结合阅读：

- [`backend/README.md`](backend/README.md)
- [`backend_front/README.md`](backend_front/README.md)
- [`front/README.md`](front/README.md)

## 快速启动

推荐启动顺序：`backend` -> `backend_front` -> `front`

### 1. 启动后端

进入 [`backend`](backend/)：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

复制环境变量模板并按本地环境修改：

```bash
copy env.example .env
```

重点配置项：

- PostgreSQL: `DATABASE_URL`
- Redis: `REDIS_URL`
- AI 模型密钥
- OCR 配置
- MinIO 配置

启动：

```bash
python run.py
```

默认地址：

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. 启动后台管理端

进入 [`backend_front`](backend_front/)：

```bash
npm install
npm run dev
```

默认通过 [`backend_front/vite.config.js`](backend_front/vite.config.js) 代理：

- `/api` -> `http://localhost:8000`
- `/ai-question` -> `http://localhost:9000`

### 3. 启动微信小程序端

进入 [`front`](front/)，使用微信开发者工具导入项目。

默认接口地址见：

- [`front/utils/config.js`](front/utils/config.js)

当前默认值：

```js
baseUrl: 'http://localhost:8000/api/v1'
```

如果使用真机调试，需要改成局域网可访问地址或部署地址。

## 开发说明

### 后端依赖的基础服务

- PostgreSQL
- Redis
- MinIO（轮播图等文件存储）

### 接口约定

- 后端统一前缀：`/api/v1`
- 统一响应格式：`code + message + data`
- 管理端同时使用 JWT 和 Session 机制
- 小程序端带有 access token / refresh token 刷新逻辑

### 典型业务流程

1. 学生在小程序上传图片或输入题目
2. 后端调用 OCR 与 AI 模型完成识别和解题
3. 结果进入用户练习/错题/学习分析链路
4. 管理端维护题库、公告、轮播图、系统配置和运营数据

## 当前项目状态

从现有代码看，项目已经不只是“AI 搜题 Demo”，而是一个正在扩展中的教学系统雏形，已覆盖：

- 用户与管理员认证
- AI 解题主链路
- 题库与知识点管理
- 公告、轮播图、系统配置
- 练习、错题本、学习分析
- 后台统计与日志

后续重点通常会落在：

- 数据闭环进一步完善
- 题库内容沉淀
- 学情评估与个性化推荐
- 更稳定的部署和联调流程

## 相关文档

- 后端接口文档：[`backend/API接口文档.md`](backend/API接口文档.md)
- 后端环境变量示例：[`backend/env.example`](backend/env.example)
- 管理端 OpenAPI 描述：[`backend_front/openapi.json`](backend_front/openapi.json)

## 适合谁阅读这个仓库

- 需要继续开发 AI 教育类产品的同学
- 负责前后端联调的开发者
- 需要快速了解项目边界、模块关系和启动方式的新成员
