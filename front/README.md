# AI智学 (AI Smart Learning)

## 项目简介

AI智学是一个基于微信小程序的智能学习辅助平台，旨在通过AI技术帮助学生更高效地进行学习、练习和复习。项目集成了AI辅导、智能刷题、错题本管理、学习分析等核心功能。

## 主要功能

*   **首页**: 展示核心功能入口及推荐内容。
*   **AI 辅导**: 提供智能问答、对话历史记录及搜索结果展示。
*   **练习刷题**: 支持多种题型的在线练习。
*   **错题本**: 自动记录错题，支持错题查看与复习。
*   **拍照搜题**: 集成相机功能，支持题目拍照与裁剪上传。
*   **学习分析**: 可视化展示学习进度与分析报告。
*   **个人中心**: 用户资料管理、设置等。

## 目录结构

```
AI_question_front/
├── pages/                  # 小程序页面目录
│   ├── ai/                 # AI相关页面（聊天、历史、搜索结果）
│   ├── analysis/           # 学习分析页面
│   ├── auth/               # 认证页面（登录、注册、找回密码）
│   ├── camera/             # 相机与裁剪页面
│   ├── home/               # 首页
│   ├── mistake/            # 错题本相关页面
│   ├── practice/           # 练习相关页面
│   ├── profile/            # 个人中心相关页面
│   └── subject/            # 学科详情页面
├── utils/                  # 工具函数目录
│   ├── api.js              # API接口封装
│   ├── request.js          # 网络请求封装
│   └── ...
├── images/                 # 图片资源目录
├── docs/                   # 项目文档目录
├── app.js                  # 小程序逻辑
├── app.json                # 小程序公共配置
├── app.wxss                # 小程序公共样式
└── project.config.json     # 项目配置文件
```

## 快速开始

### 环境准备

1.  下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)。
2.  申请微信小程序账号，获取 AppID。

### 运行项目

1.  打开微信开发者工具。
2.  选择“导入项目”，指向本项目根目录 `AI_question_front`。
3.  在 `AppID` 栏输入你的小程序 AppID（本项目默认 AppID 为 `wx943b929386c7ff10`，如无权限请替换为自己的测试号或申请权限）。
4.  点击“确定”进入开发者工具界面，即可预览和调试。

## 配置说明

*   **API 配置**: 后端接口地址通常在 `utils/config.js` 或 `utils/request.js` 中配置，请根据实际后端服务地址进行修改。
*   **项目配置**: `project.config.json` 包含了项目的编译配置和开发者工具设置。

## 接口文档

详细的前端接口文档请参考 [docs/frontend_api.md](docs/frontend_api.md)。

## 技术栈

*   **前端框架**: 微信小程序原生开发 (WXML, WXSS, JS/JSON)
*   **组件库**: Glass Easel (部分组件)
*   **样式**: WXSS (类似 CSS)

## 贡献指南

欢迎提交 Issue 或 Pull Request 来改进本项目。

## 许可证

MIT License
