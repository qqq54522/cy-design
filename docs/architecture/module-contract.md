# 模块接入协议

## 概述

所有业务模块接入灵桥 Creative Hub 平台，必须遵守本协议。平台通过 `config/modules.json` 统一注册和管理模块。

## 模块注册字段

每个模块在 `config/modules.json` 中注册时，需提供以下字段：

```json
{
  "key": "content",
  "name": "素材抓取",
  "description": "热点选题、文案生成与视觉物料生成",
  "route": "/content",
  "defaultPath": "/hot",
  "nav": [
    { "path": "/hot", "label": "热搜中心" }
  ],
  "frontend": {
    "port": 5174,
    "origin": "http://localhost:5174",
    "cwd": "素材抓取/content-marketing/frontend"
  },
  "backend": {
    "port": 8001,
    "origin": "http://localhost:8001",
    "cwd": "素材抓取/content-marketing/backend",
    "healthPath": "/health",
    "uvicornModule": "app.main:app"
  }
}
```

## 健康检查协议

每个模块后端必须实现 `GET /health` 接口：

```json
{
  "status": "healthy",
  "module": "content-marketing",
  "version": "1.0.0"
}
```

## API 响应格式

所有模块 API 必须遵守统一响应格式（定义在 `shared/backend/core/responses.py`）：

### 成功响应
```json
{ "success": true, "message": "ok", "data": { ... } }
```

### 错误响应
```json
{ "success": false, "error": { "code": "NOT_FOUND", "message": "资源不存在" } }
```

### 分页响应
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 目录结构约定

```
模块名/
├── frontend/          # 前端（React + Vite）
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/           # 后端（FastAPI）
│   ├── app/
│   │   ├── api/       # 路由层
│   │   ├── services/  # 服务层
│   │   ├── models/    # 数据模型
│   │   ├── core/      # 核心能力
│   │   ├── config.py
│   │   └── main.py
│   └── requirements.txt
└── data/              # 运行时数据（gitignore）
```

## 异常处理约定

- 业务异常继承 `shared.backend.core.exceptions.AppError`
- 错误码前缀：`PLATFORM_*`、`CONTENT_*`、`KV_*`、`EMOJI_*`
