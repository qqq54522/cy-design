# 架构概览

## 系统定位

灵桥 Creative Hub 是一个统一创意内容生产平台，整合多个 AI 驱动的内容生成模块。

## 架构分层

```
┌─────────────────────────────────────────────────┐
│                  Hub 前端 (React)                 │
│              frontend/ — 端口 5180                │
├─────────────────────────────────────────────────┤
│              平台 API (FastAPI)                   │
│           platform_api/ — 端口 8100               │
├──────────┬──────────┬──────────┬────────────────┤
│ 素材抓取  │  KV 生成  │  表情包   │  未来模块...    │
│ 8001/5174│ 8002/5175│ 8003/5176│               │
├──────────┴──────────┴──────────┴────────────────┤
│                共享层 (shared/)                    │
│          frontend/ — 组件/hooks/工具              │
│          backend/  — 异常/配置/存储/日志           │
└─────────────────────────────────────────────────┘
```

## 核心目录

| 目录 | 职责 |
|------|------|
| `frontend/` | Hub 前端壳层，负责模块导航、状态聚合、项目中心 |
| `platform_api/` | 平台后端，负责模块注册、健康检查、项目索引聚合 |
| `素材抓取/content-marketing/` | 热搜内容分析 + 营销素材生成模块 |
| `KV生成/` | 活动主视觉 KV 海报生成模块 |
| `表情包/` | AI 表情包生成模块 |
| `shared/frontend/` | 前端共享组件、hooks、工具函数、类型定义 |
| `shared/backend/` | 后端共享异常模型、基础配置、存储工具、日志配置 |
| `config/` | 模块注册配置（modules.json） |
| `docs/` | 项目文档 |
| `scripts/` | 开发/构建/运维脚本 |
| `tests/` | 跨模块测试 |

## 技术栈

### 前端
- React 19 + TypeScript 5.8
- Vite 6 构建
- Tailwind CSS 4
- Zustand 状态管理
- pnpm workspace monorepo

### 后端
- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2 + pydantic-settings
- structlog 结构化日志
- aiofiles 异步文件操作

### 基础设施
- Docker Compose (dev / prod)
- ESLint 10 + Prettier 3 (前端)
- Ruff (后端)
- Husky + lint-staged (pre-commit)

## 模块通信

- Hub 前端通过 iframe / 路由嵌入各模块前端
- 平台 API 通过 HTTP 调用各模块后端的健康检查和项目索引接口
- 各模块后端独立运行，通过 `config/modules.json` 注册到平台
