# AI智能学习系统后端

以AI解题为入口，以知识点掌握度为核心，为中小学生提供真正"因材施教"的智能学习系统。

## 功能模块

### 已实现
- ✅ 用户系统
  - 手机号/邮箱注册登录
  - JWT Token认证（普通用户）
  - Session Cookie认证（管理员）
  - SM4统一加密
- ✅ 管理员系统
  - 手机号/邮箱注册
  - 手机号/邮箱登录（密码/验证码）
  - 管理员信息管理
  - 管理员CRUD
  - 用户管理（查看/启用/禁用）
- ✅ AI搜题模块
  - 阿里云OCR题目识别
  - 多AI厂商解题（通义、DeepSeek、Kimi）
  - 图片上传识别
  - 文本直接解题

### 待实现
- ⬜ 学科与知识体系
- ⬜ 题库与内容系统
- ⬜ 个性化学习与自适应系统
- ⬜ 练习与刷题系统
- ⬜ 错题本与学习沉淀
- ⬜ 学习分析与成长反馈
- ⬜ AI使用与安全
- ⬜ 系统与基础能力

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL (异步)
- **缓存**: Redis
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + Session
- **加密**: SM4 (AES-128)
- **OCR**: 阿里云OCR（题目识别）
- **AI模型**: 通义千问、DeepSeek、Kimi

## 项目架构

```
app/
├── api/                    # API层：路由和接口定义
│   └── v1/                 # API v1版本
│       ├── auth.py         # 认证接口（注册、登录、登出）
│       ├── user.py         # 用户信息管理接口
│       ├── admin.py        # 管理员接口
│       └── question.py     # 搜题接口
├── common/                 # 通用模块
│   ├── exceptions.py       # 自定义异常
│   ├── response.py         # 统一响应格式
│   └── utils.py            # 工具函数
├── core/                   # 核心模块
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接
│   ├── redis.py            # Redis连接
│   ├── ai/                 # AI核心模块
│   │   ├── ocr.py          # OCR识别服务
│   │   └── models.py       # AI模型服务
│   └── security/           # 安全模块
│       ├── jwt.py          # JWT认证
│       ├── session.py      # Session管理
│       ├── sm4.py          # SM4加密
│       └── password.py     # 密码处理
├── middleware/             # 中间件
│   ├── auth.py             # 认证中间件
│   └── exception_handler.py  # 异常处理
├── models/                 # 数据模型层
│   └── user.py             # 用户模型
├── repositories/           # 数据访问层
│   └── user.py             # 用户仓储
├── schemas/                # Pydantic模式层
│   ├── user.py             # 用户Schema
│   ├── admin.py            # 管理员Schema
│   └── question.py         # 搜题Schema
├── services/               # 业务逻辑层
│   ├── user.py             # 用户服务
│   ├── verify_code.py      # 验证码服务
│   ├── admin.py            # 管理员服务
│   └── question.py         # 搜题服务
└── main.py                 # 应用入口
```

## 分层架构说明

```
┌─────────────────────────────────────────┐
│              API Layer                   │  <- 接收请求，返回响应
├─────────────────────────────────────────┤
│           Service Layer                  │  <- 业务逻辑处理
├─────────────────────────────────────────┤
│         Repository Layer                 │  <- 数据访问封装
├─────────────────────────────────────────┤
│            Model Layer                   │  <- 数据模型定义
├─────────────────────────────────────────┤
│            Core Layer                    │  <- 基础设施
└─────────────────────────────────────────┘
```

- **上层依赖下层，下层不依赖上层**
- **功能解耦，职责单一**

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑.env文件，配置数据库和Redis连接信息
```

### 3. 初始化数据库

```bash
# 创建数据库表并创建初始管理员
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式启动
python scripts/run.py

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/verify-code/send | 发送验证码 |
| POST | /api/v1/auth/register/phone | 手机号注册 |
| POST | /api/v1/auth/register/email | 邮箱注册 |
| POST | /api/v1/auth/login/password | 密码登录 |
| POST | /api/v1/auth/login/verify-code | 验证码登录 |
| POST | /api/v1/auth/token/refresh | 刷新Token |
| POST | /api/v1/auth/logout | 退出登录 |
| POST | /api/v1/auth/password/reset | 重置密码 |

### 用户接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/user/info | 获取用户信息 |
| PUT | /api/v1/user/info | 更新用户信息 |
| POST | /api/v1/user/password/change | 修改密码 |
| POST | /api/v1/user/bind/phone | 绑定手机号 |
| POST | /api/v1/user/bind/email | 绑定邮箱 |

### 管理员接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/admin/register/phone | 手机号注册管理员 |
| POST | /api/v1/admin/register/email | 邮箱注册管理员 |
| POST | /api/v1/admin/login/password | 管理员密码登录 |
| POST | /api/v1/admin/login/verify-code | 管理员验证码登录 |
| POST | /api/v1/admin/logout | 管理员登出 |
| GET | /api/v1/admin/me | 获取当前管理员信息 |
| PUT | /api/v1/admin/me | 更新当前管理员信息 |
| POST | /api/v1/admin/me/password | 修改管理员密码 |
| GET | /api/v1/admin/list | 获取管理员列表 |
| POST | /api/v1/admin | 创建管理员 |
| GET | /api/v1/admin/{id} | 获取管理员详情 |
| PUT | /api/v1/admin/{id} | 更新管理员 |
| POST | /api/v1/admin/{id}/reset-password | 重置管理员密码 |
| DELETE | /api/v1/admin/{id} | 删除管理员 |
| GET | /api/v1/admin/users/list | 获取用户列表 |
| GET | /api/v1/admin/users/{id} | 获取用户详情 |
| PUT | /api/v1/admin/users/{id}/status | 更新用户状态 |

### 搜题接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/question/solve/image | 从图片URL/Base64识别并解题 |
| POST | /api/v1/question/solve/image/upload | 上传图片识别并解题 |
| POST | /api/v1/question/solve/text | 从文本直接解题 |
| GET | /api/v1/question/providers | 获取可用的AI提供商列表 |

## 统一响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": {}
}
```

### 分页响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": [],
    "page_info": {
        "page": 1,
        "page_size": 20,
        "total": 100,
        "total_pages": 5
    }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1000 | 未知错误 |
| 1001 | 参数错误 |
| 1003 | 禁止访问 |
| 2001 | 未授权 |
| 2002 | Token已过期 |
| 2003 | Token无效 |
| 2004 | Session已过期 |
| 2005 | Session无效 |
| 3001 | 用户不存在 |
| 3002 | 用户已存在 |
| 3003 | 密码错误 |
| 3006 | 验证码错误 |
| 3008 | 用户已禁用 |
| 4001 | 管理员不存在 |
| 4002 | 管理员已存在 |
| 4003 | 管理员密码错误 |
| 4004 | 管理员已禁用 |
| 4005 | 权限不足 |

## 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## License

MIT

