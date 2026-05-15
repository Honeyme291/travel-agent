# 🗺️ 智慧旅行 Agent 系统

> 基于 **LangGraph + FastAPI + React + MCP** 的 AI 智慧旅行规划平台
> 支持微信公众号接入 · 多轮对话 · 长期记忆 · 路线可视化 · 景点图片

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![LangChain](https://img.shields.io/badge/LangChain-1.2-green)](https://langchain.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed)](https://docker.com)

---

## 目录

- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [MCP 工具生态](#mcp-工具生态)
- [Agent 工作流](#agent-工作流)
- [数据库设计](#数据库设计)
- [微信公众号接入](#微信公众号接入)
- [Docker 部署](#docker-部署)
- [环境变量](#环境变量)
- [开发路线图](#开发路线图)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 微信公众号 │  │  React Web   │  │  第三方 API 调用   │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│       │               │                   │             │
├───────┼───────────────┼───────────────────┼─────────────┤
│       ▼               ▼                   ▼             │
│  ┌─────────────────────────────────────────────────┐   │
│  │                 Nginx 网关                       │   │
│  └─────────────────────┬───────────────────────────┘   │
│                        │                                │
├────────────────────────┼────────────────────────────────┤
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FastAPI 应用层                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐│   │
│  │  │ WeChat   │ │ Auth JWT │ │ Chat API (REST   ││   │
│  │  │ Handler  │ │ 登录/注册 │ │  + SSE Stream)   ││   │
│  │  └──────────┘ └──────────┘ └──────────────────┘│   │
│  └─────────────────────┬───────────────────────────┘   │
│                        │                                │
├────────────────────────┼────────────────────────────────┤
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │            LangGraph Agent 编排层                 │   │
│  │  Planner → Weather → Route → Fortune → Image     │   │
│  └──────┬──────────────┬──────────────┬────────────┘   │
│         │              │              │                 │
├────────┼──────────────┼──────────────┼─────────────────┤
│        ▼              ▼              ▼                 │
│  ┌──────────┐  ┌───────────┐  ┌───────────────┐      │
│  │ Redis    │  │PostgreSQL │  │ MCP Servers   │      │
│  │ Session  │  │ 持久化存储  │  │ 4 个外部服务   │      │
│  └──────────┘  └───────────┘  └───────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### 核心设计原则

| 原则 | 实现 |
|------|------|
| **前后端分离** | FastAPI RESTful API + React SPA，通过 JWT 鉴权 |
| **Agent 编排** | LangGraph 工作流：Planner 意图识别 → 并行 Agent 执行 → 综合回复 |
| **工具即服务** | MCP (Model Context Protocol) 标准化外部工具接入，每个工具独立 `.py` 文件 |
| **双存储** | Redis 缓存热数据（7天 TTL）+ PostgreSQL 持久化全量历史 |
| **优雅降级** | LLM 不可用时正则兜底提取目的地；MCP 不可用时返回友好错误提示 |

---

## 技术栈

### 后端

| 模块 | 技术 | 说明 |
|------|------|------|
| Web 框架 | **FastAPI** 0.115 | 异步 HTTP，自动 OpenAPI 文档 |
| Agent 框架 | **LangGraph** 0.2 | 状态图工作流，多 Agent 编排 |
| LLM | **Qwen-Plus** (DashScope) | 阿里云兼容 OpenAI 协议 |
| Embedding | **text-embedding-v3** (DashScope) | RAG 向量化 |
| RAG 向量库 | **Chroma** | 轻量级本地向量存储 |
| ORM | **SQLAlchemy 2.0** (async) | PostgreSQL 异步驱动 |
| 缓存 | **Redis 7** | Session 缓存 + 对话上下文 |
| MCP SDK | **mcp 1.27** | streamable HTTP + SSE 双协议 |
| 认证 | **PyJWT** | JWT Token 签发/验证 |
| 服务器 | **Uvicorn** | ASGI 生产服务器 |

### 前端

| 模块 | 技术 | 说明 |
|------|------|------|
| 框架 | **React 18** | 函数组件 + Hooks |
| 构建 | **Vite 4** | 极速 HMR，ESBuild 打包 |
| Markdown | **react-markdown** | 流式 AI 回复渲染 |
| 地图 | **@uiw/react-amap** | 高德地图 React 组件 |
| HTTP | **Fetch API + SSE** | REST 请求 + EventSource 流式 |
| 样式 | **CSS Variables** | 无第三方 UI 库，纯 CSS 设计 |

---

## 功能特性

### 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 智能旅行规划 | ✅ | LangGraph 多 Agent 编排，支持简单/复杂/多目的地三种场景 |
| 天气查询 | ✅ | MCP 接入高德地图，每个目的地独立查询 |
| 火车票查询 | ✅ | MCP 接入 12306，自动获取站点代码 + 车票 |
| 酒店搜索 | ✅ | MCP 高德 POI 搜索，按城市/关键词 |
| 自驾路线 | ✅ | 高德驾车路径规划，距离/时间预估 |
| 公交路线 | ✅ | 高德公交换乘规划 |
| 黄历吉日 | ✅ | MCP 接入八字黄历，出行择日分析 |
| 景点图片 | ✅ | Wikimedia Commons MCP 搜索，图左 + 描述右布局 |
| 流式输出 | ✅ | SSE (Server-Sent Events) 实时推送 |
| 多轮对话 | ✅ | LangChain ConversationBufferMemory + Redis 缓存 |
| 长期记忆 | ✅ | PostgreSQL 持久化全量历史，按用户/会话检索 |
| 用户系统 | ✅ | JWT 登录/注册，OpenID 绑定 |
| 微信公众号 | ✅ | XML 消息解析，签名验证，图文消息回复 |
| Docker 部署 | ✅ | Nginx + Backend + Frontend + Redis + PostgreSQL |

---

## 快速开始

### 前置条件

- Python ≥ 3.11
- Node.js ≥ 18
- Docker & Docker Compose（用于 Redis / PostgreSQL）
- DashScope API Key（阿里云百炼平台）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/wechat-travel-agent.git
cd wechat-travel-agent
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入以下关键配置：
#   DASHSCOPE_API_KEY  - 必须，阿里云百炼 API Key
#   PEXELS_KEY         - 可选，Pexels 图片 API
#   WIKIMEDIA_APIKEY   - 可选，Wikimedia MCP 图片搜索
#   WECHAT_TOKEN       - 可选，微信公众号 Token
```

### 3. 启动基础设施 (Redis + PostgreSQL)

```bash
docker compose up -d redis postgres
```

### 4. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
# → http://localhost:8000
# → API 文档: http://localhost:8000/docs
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 6. 一键 Docker 部署

```bash
docker compose up -d
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# 微信回调: http://your-domain/wechat/callback
```

---

## 项目结构

```
wechat-travel-agent/
│
├── backend/                          # FastAPI 后端 (Python)
│   ├── run.py                        # 启动入口: uvicorn
│   ├── requirements.txt              # Python 依赖 (21 个包)
│   ├── .env                          # 环境变量（不提交 Git）
│   └── app/
│       ├── main.py                   # FastAPI 应用 + 生命周期
│       │
│       ├── config/                   # 配置层
│       │   ├── settings.py           # 全局配置（环境变量读取）
│       │   └── mcp_servers.py        # MCP 服务器 URL 注册
│       │
│       ├── core/                     # 核心层
│       │   ├── llm.py                # LLM 初始化（Qwen-Plus）
│       │   ├── rag.py                # RAG 检索器（Chroma + Embedding）
│       │   ├── agent.py              # ReAct Agent 构建 + 执行
│       │   └── memory.py             # 对话记忆（ConversationBufferMemory）
│       │
│       ├── agent/                    # LangGraph 多 Agent 层
│       │   ├── workflow.py           # 主工作流编排 (Planner → 并行 → 汇总)
│       │   ├── planner.py            # 意图识别 + 任务分配
│       │   ├── weather_agent.py      # 天气查询 Agent
│       │   ├── route_agent.py        # 路线规划 Agent
│       │   ├── image_agent.py        # 图片搜索 Agent (Wikimedia MCP)
│       │   ├── fortune_agent.py      # 黄历分析 Agent
│       │   └── memory_agent.py       # 长期记忆 Agent (DB + Redis)
│       │
│       ├── tools/                    # MCP 工具层（每个工具一个文件）
│       │   ├── base.py               # 工具基类 + run_async 桥接 + parse_tool_input
│       │   ├── mcp_manager.py        # MCP 连接管理器（顺序连接 + 超时重试）
│       │   ├── registry.py           # 工具注册中心（工厂模式）
│       │   ├── train_query.py        # 🚂 12306 火车票查询
│       │   ├── weather.py            # ☀️ 高德天气
│       │   ├── geo.py                # 📍 高德地理编码
│       │   ├── hotel.py              # 🏨 高德酒店搜索
│       │   ├── poi.py                # 🔍 高德 POI 搜索
│       │   ├── driving.py            # 🚗 高德驾车路线
│       │   ├── transit.py            # 🚌 高德公交路线
│       │   ├── lucky_day.py          # 🗓️ 黄历查询
│       │   └── r1_analysis.py        # 🧠 LLM 深度分析
│       │
│       ├── api/                      # API 路由层
│       │   ├── router.py             # 路由汇总
│       │   ├── chat.py               # POST /api/chat + GET /api/spot-images
│       │   ├── stream.py             # GET /api/chat/stream (SSE)
│       │   ├── auth.py               # POST /api/auth/register + /login
│       │   ├── history.py            # 历史会话 CRUD
│       │   ├── session.py            # 会话管理
│       │   ├── tools.py              # 工具列表
│       │   ├── health.py             # 健康检查
│       │   └── wechat.py             # 微信公众号回调
│       │
│       ├── services/                 # 业务服务层
│       │   ├── travel_service.py     # 核心旅行规划编排
│       │   └── pre_analyzer.py       # 场景预分析（simple/complex/multi-dest）
│       │
│       ├── schemas/                  # 数据模型
│       │   └── models.py             # Pydantic 请求/响应 Schema
│       │
│       ├── models/                   # 数据库模型
│       │   ├── database.py           # SQLAlchemy async 引擎
│       │   ├── user.py               # User 表
│       │   ├── conversation.py       # Conversation 表
│       │   ├── message.py            # Message 表
│       │   └── travel_route.py       # TravelRoute 表
│       │
│       ├── memory/                   # 缓存层
│       │   └── redis_session.py      # Redis Session 管理 (7天 TTL)
│       │
│       ├── utils/                    # 工具层
│       │   ├── map_utils.py          # 高德静态地图 URL 生成
│       │   ├── image_utils.py        # 图片下载 + 缓存
│       │   └── jwt_utils.py          # JWT Token 签发 + 验证
│       │
│       └── wechat/                   # 微信公众号层
│           ├── crypto.py             # SHA1 签名验证
│           └── handler.py            # XML 解析 + 消息路由
│
├── frontend/                         # React 前端 (Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                # API 代理到 :8000
│   └── src/
│       ├── main.jsx                  # ReactDOM 入口
│       ├── App.jsx                   # 主组件（Auth Gate + 聊天 + 图片）
│       ├── api/client.js             # API 客户端（REST + SSE + JWT）
│       ├── styles/index.css          # 全局样式（CSS Variables）
│       └── components/
│           ├── LoginPage.jsx         # 登录页（登录/注册双 Tab）
│           ├── Sidebar.jsx           # 侧边栏（用户/历史/工具/MCP状态）
│           ├── ChatMessage.jsx       # 消息气泡（Markdown + 景点卡片）
│           ├── ChatInput.jsx         # 输入框（Enter 发送）
│           ├── TravelCard.jsx        # 景点卡片（图左 + 文右）
│           ├── RouteMap.jsx          # 路线地图
│           └── HistoryList.jsx       # 历史会话列表
│
├── docker/                           # Docker 部署
│   ├── Dockerfile.backend            # Python 后端镜像
│   ├── Dockerfile.frontend           # Node + Nginx 前端镜像
│   ├── nginx.conf                    # Nginx 反向代理配置
│   └── init.sql                      # PostgreSQL 初始化 DDL
│
├── docker-compose.yml                # 5 服务编排
├── .env.example                      # 环境变量模板
└── README.md                         # 本文档
```

---

## API 文档

启动后端后访问 `http://localhost:8000/docs` 查看 Swagger UI。

### 端点总览

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| `POST` | `/api/auth/register` | - | 用户注册，返回 JWT |
| `POST` | `/api/auth/login` | - | 用户登录，返回 JWT |
| `GET` | `/api/auth/me` | - | Token 验证，返回用户信息 |
| `POST` | `/api/chat` | - | 旅行规划对话（自动返回景点卡片） |
| `GET` | `/api/chat/stream` | - | SSE 流式对话 |
| `GET` | `/api/spot-images` | - | 单独查询景点图片 |
| `GET` | `/api/tools` | - | 可用工具列表 |
| `GET` | `/api/health` | - | 健康检查 + MCP 服务器状态 |
| `POST` | `/api/session/new` | - | 创建新会话 |
| `POST` | `/api/session/clear` | - | 清除会话记忆 |
| `GET` | `/api/history/conversations` | - | 用户历史对话列表 |
| `GET` | `/api/history/messages` | - | 指定会话的消息 |
| `DELETE` | `/api/history/conversations/{id}` | - | 删除对话 |
| `GET` | `/wechat/callback` | - | 微信公众号服务器验证 |
| `POST` | `/wechat/callback` | - | 微信公众号消息回调 |

---

## MCP 工具生态

系统通过 MCP (Model Context Protocol) 接入 4 个外部服务：

| MCP Server | 协议 | 工具数 | 说明 |
|-----------|------|--------|------|
| **amap-maps** | streamable HTTP | 12 | 高德地图：天气/地理编码/POI/驾车/公交/步行/骑行/距离 |
| **12306-mcp** | streamable HTTP | 8 | 12306 火车票：站点代码/车票查询/中转/经停站 |
| **Bazi-MCP** | streamable HTTP | 3 | 八字黄历：黄历查询/八字详情/阳历时间 |
| **wikimedia_search_images** | SSE | 1 | Wikimedia Commons 图片搜索 |

### Agent 可见工具

| 工具名 | MCP Server | 远程工具 | 功能 |
|--------|-----------|----------|------|
| `train_query` | 12306-mcp | `get-tickets` | 火车票查询（自动含自驾路线） |
| `train_station_code` | 12306-mcp | `get-stations-code-in-city` | 城市站点代码 |
| `gaode_weather` | amap-maps | `maps_weather` | 天气查询 |
| `gaode_geo` | amap-maps | `maps_geo` | 地理编码（地址→坐标） |
| `gaode_hotel_search` | amap-maps | `maps_text_search` | 酒店搜索 |
| `gaode_poi_search` | amap-maps | `maps_text_search` | POI 兴趣点搜索 |
| `gaode_around_search` | amap-maps | `maps_around_search` | 周边搜索 |
| `gaode_driving` | amap-maps | `maps_direction_driving` | 驾车路线 |
| `gaode_transit` | amap-maps | `maps_direction_transit_integrated` | 公交路线 |
| `gaode_distance` | amap-maps | `maps_distance` | 距离计算 |
| `lucky_day` | Bazi-MCP | `getChineseCalendar` | 黄历吉日 |
| `r1_analysis` | - (LLM) | - | 深度旅行分析 |

---

## Agent 工作流

```
用户输入: "我想去杭州西湖玩3天，预算2000"
    │
    ▼
┌──────────────────────┐
│   Planner (意图识别)   │
│   提取: 目的地/天数/预算  │
│   决策: need_tools=true │
│   Tasks: [weather,      │
│          train, hotel,   │
│          fortune, image] │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│        并行 Agent 执行                │
│                                      │
│  Weather Agent  → 杭州天气 + 建议     │
│  Route Agent    → 出发地→杭州交通     │
│  Hotel Agent    → 杭州酒店搜索        │
│  Fortune Agent  → 出发日黄历分析      │
│  Image Agent    → 西湖景点图片        │
│                                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────┐
│   综合回复生成 (LLM)   │
│   结构化 Markdown      │
│   + 景点卡片 (图+文)   │
└──────────────────────┘
```

---

## 数据库设计

### ER 图

```
┌──────────┐       ┌───────────────┐       ┌──────────┐
│  users   │──1:N──│ conversations │──1:N──│ messages │
└──────────┘       └───────────────┘       └──────────┘
                           │
                           └──1:N──┌──────────────┐
                                   │ travel_routes│
                                   └──────────────┘
```

### 表结构

**users** — 用户表
```sql
id         BIGSERIAL PRIMARY KEY
openid     VARCHAR(128) UNIQUE   -- 微信 OpenID / 用户名
nickname   VARCHAR(128)
avatar     TEXT
created_at TIMESTAMP DEFAULT NOW()
```

**conversations** — 对话表
```sql
id          BIGSERIAL PRIMARY KEY
session_id  VARCHAR(128) NOT NULL INDEX
user_id     BIGINT REFERENCES users(id)
title       VARCHAR(255)          -- 自动设为用户第一条输入
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

**messages** — 消息表
```sql
id               BIGSERIAL PRIMARY KEY
conversation_id  BIGINT REFERENCES conversations(id) ON DELETE CASCADE
role             VARCHAR(32)     -- 'user' | 'assistant'
content          TEXT
extra_data       JSONB           -- 扩展元数据
created_at       TIMESTAMP
```

**travel_routes** — 旅行路线表
```sql
id               BIGSERIAL PRIMARY KEY
conversation_id  BIGINT REFERENCES conversations(id)
session_id       VARCHAR(128)
route_json       JSONB           -- 路线数据
map_image        TEXT            -- 地图图片 URL
created_at       TIMESTAMP
```

---

## 微信公众号接入

### 配置步骤

1. 在微信公众平台 → 设置与开发 → 服务器配置
2. URL: `https://your-domain.com/wechat/callback`
3. Token: 与 `.env` 中 `WECHAT_TOKEN` 一致
4. 消息加解密方式: 明文模式

### 支持的消息类型

| 类型 | 说明 |
|------|------|
| `text` | 文本消息 → 调用 Agent 生成回复 |
| `event.subscribe` | 关注事件 → 自动发送欢迎消息 |
| `news` | 图文消息 → 景点卡片推送 |

---

## Docker 部署

### 服务编排

```yaml
services:
  nginx     # 反向代理:80/443, WeChat 回调入口
  backend   # FastAPI:8000, MCP 初始化 + REST API
  frontend  # React SPA:3000 (dev) / Nginx 静态 (prod)
  redis     # Redis:6379, Session 缓存
  postgres  # PostgreSQL:5432, 持久化存储
```

### 一键部署

```bash
# 启动全部服务
docker compose up -d

# 查看日志
docker compose logs -f backend

# 停止
docker compose down
```

---

## 环境变量

完整配置见 `.env.example`：

| 变量 | 必须 | 说明 |
|------|------|------|
| `DASHSCOPE_API_KEY` | ✅ | 阿里云百炼 API Key (Qwen LLM + Embedding) |
| `DEEPSEEK_API_KEY` | - | DeepSeek API Key (备选 R1 分析) |
| `POSTGRES_URL` | ✅ | PostgreSQL 连接串 (asyncpg) |
| `REDIS_URL` | ✅ | Redis 连接串 |
| `JWT_SECRET` | ✅ | JWT 签名密钥 |
| `WECHAT_APPID` | - | 微信公众号 AppID |
| `WECHAT_SECRET` | - | 微信公众号 AppSecret |
| `WECHAT_TOKEN` | - | 微信公众号 Token |
| `WIKIMEDIA_APIKEY` | - | Wikimedia MCP API Key (xiaobenyang.com) |
| `PEXELS_KEY` | - | Pexels 图片 API Key |
| `UNSPLASH_KEY` | - | Unsplash 图片 API Key |
| `AMAP_KEY` | - | 高德地图 Web API Key |

---

## 开发路线图

- [x] LangGraph 多 Agent 工作流
- [x] MCP 4 服务器集成 (23 个工具)
- [x] React 登录/注册 + 历史会话
- [x] SSE 流式输出
- [x] Redis + PostgreSQL 双存储
- [x] 微信公众号 XML 消息处理
- [x] Docker Compose 5 服务编排
- [x] 景点图片搜索 (Wikimedia + Pexels)
- [x] JWT 认证体系
- [ ] RAG 旅游知识库 (Milvus)
- [ ] 多 Agent 协作 (CrewAI)
- [ ] AI 语音导游 (TTS)
- [ ] 数字人导游 (Live2D)
- [ ] 语音输入 (Whisper)
- [ ] CI/CD Pipeline
- [ ] Kubernetes Helm Chart

---

## License

MIT
