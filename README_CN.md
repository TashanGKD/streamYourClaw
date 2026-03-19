# streamYourClaw

<div align="center">

**开源 AI Agent 直播系统 - 在 TikTok 实时直播你的 AI 执行过程**

由一个始终坚定任务的主管 Agent 监督 OpenClaw 的每一次执行结果，并根据状态让它进一步执行任务，永远不停。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](README.md) | [中文文档](#概述)

</div>

---

## 概述

streamYourClaw 让你能够在 TikTok 上实时直播 AI Agent 执行任务的过程。系统特点：

- **永续执行** - 主管 Agent 监督 OpenClaw 持续执行任务，永不停歇
- **实时可视化** - 通过 TikTok 直播展示 AI 的思考过程
- **社区驱动** - 所有模块都可通过 Pull Request 贡献
- **可插拔架构** - 易于扩展新的 Agent、主题和内容

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    观众层                                │
│          TikTok直播 ← OBS ← 前端网页                    │
└─────────────────────────────────────────────────────────┘
                         ↓ WebSocket
┌─────────────────────────────────────────────────────────┐
│                   后端服务                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FastAPI 应用                                    │   │
│  │  ├── 状态引擎 (核心调度器)                       │   │
│  │  ├── Agent 编排器                               │   │
│  │  └── WebSocket 网关                             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓ Redis Streams
┌─────────────────────────────────────────────────────────┐
│                   Agent 工作层                           │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   主管       │ ←─────→ │   OpenClaw   │             │
│  │  (监督者)    │         │   (执行者)   │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- Redis 服务器
- (可选) Docker & Docker Compose

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/streamYourClaw.git
cd streamYourClaw

# 安装依赖
pip install -e ".[dev]"

# 启动 Redis (使用 Docker)
docker run -d -p 6379:6379 redis:alpine

# 启动后端服务
cd backend
uvicorn app.main:app --reload --port 8000
```

### 访问前端

打开浏览器访问 `http://localhost:8000`

### TikTok 直播设置

1. 打开 OBS Studio
2. 添加"浏览器"源
3. 设置 URL 为 `http://localhost:8000`
4. 设置分辨率为 1080x1920 (9:16 竖屏)
5. 开始推流到 TikTok

## 项目结构

```
streamYourClaw/
├── frontend/              # 前端网页 (HTML/CSS/JS)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
│       └── videos/        # 状态视频素材
│           └── meta.json  # 视频配置文件
│
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/          # REST & WebSocket 接口
│   │   ├── core/         # 状态引擎、消息队列
│   │   ├── agents/       # Agent 模块 (可插拔)
│   │   └── models/       # 数据模型
│   └── tests/
│
├── sdk/                   # 贡献者 SDK
│   └── python/
│
├── docs/                  # 文档
│   └── contributing/      # 贡献指南
│
└── scripts/               # 工具脚本
```

## 功能特性

### 状态引擎

核心调度器，负责：
- 任务生命周期和执行流程管理
- 通过 Redis Streams 进行 Agent 间通信
- 实时状态广播到前端

### 主管 Agent (Supervisor)

一个 AI Agent，负责：
- 将任务分解为子任务
- 审核 OpenClaw 的执行结果
- 决定下一步行动（继续、重试、失败）
- 提供改进反馈

### OpenClaw 集成

预留给 OpenClaw 的接口：
- 当前以模拟模式运行，用于演示
- 已准备好对接真实 OpenClaw

### 可视化组件

- **思维导图**：展示任务层级和进度
- **状态视频**：用动画视频展示 Agent 状态
- **思考日志**：实时显示 Agent 的思考过程

## 贡献指南

我们欢迎各种贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 快速贡献指南

| 贡献类型 | 方法 |
|---------|------|
| 状态视频 | 添加 MP4 到 `frontend/assets/videos/`，更新 `meta.json` |
| Agent 模块 | 在 `backend/app/agents/` 创建 Agent，继承 `BaseAgent` |
| 主题样式 | 添加 CSS 到 `frontend/css/themes/` |
| 代码 | Fork → 分支 → PR |

详细指南：
- [贡献视频](docs/contributing/videos.md)
- [贡献 Agent](docs/contributing/agents.md)
- [贡献主题](docs/contributing/themes.md)

## API 参考

### REST 接口

| 方法 | 端点 | 描述 |
|-----|------|------|
| GET | `/api/` | API 信息 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/status` | 系统状态 |
| POST | `/api/task` | 提交新任务 |
| GET | `/api/task/{id}` | 获取任务详情 |
| GET | `/api/tasks` | 列出最近任务 |
| GET | `/api/agents` | 列出已注册 Agent |

### WebSocket

连接 `/ws` 获取实时更新：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // 处理 state:broadcast, log:broadcast, mindmap:broadcast
};
```

## 配置

环境变量 (`.env`)：

```bash
# 应用配置
APP_NAME=streamYourClaw
DEBUG=false

# 服务器
HOST=0.0.0.0
PORT=8000

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM (用于主管 Agent)
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
SUPERVISOR_MODEL=gpt-4
```

## Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 或手动构建
docker build -t streamyourclaw .
docker run -p 8000:8000 streamyourclaw
```

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 使用 [FastAPI](https://fastapi.tiangolo.com/) 构建
- 灵感来源于 AI Agent 可视化需求
- 欢迎社区贡献

---

<div align="center">

由 streamYourClaw 社区用 ❤️ 制作

</div>