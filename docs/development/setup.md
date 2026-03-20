# 本地开发环境搭建

## 前置要求

| 工具 | 版本要求 |
|------|---------|
| Node.js | >= 18.0.0 |
| pnpm | >= 8.0.0 |
| Python | >= 3.11 |

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入必要的 API Key
```

### 2. 安装前端依赖

```bash
pnpm install
```

### 3. 安装后端依赖

```bash
pip install -r platform_api/requirements.txt
pip install -r 素材抓取/content-marketing/backend/requirements.txt
pip install -r KV生成/backend/requirements.txt
pip install -r 表情包/backend/requirements.txt
```

### 4. 启动

```powershell
.\start.ps1                        # 启动所有服务
.\scripts\dev-platform.ps1         # 仅启动平台层
.\scripts\dev-module.ps1 kv        # 启动指定模块
.\scripts\check-env.ps1            # 环境自检
```

### 5. 访问地址

| 服务 | 地址 |
|------|------|
| Hub 前端 | http://localhost:5180 |
| 平台 API | http://localhost:8100 |
| 素材抓取 | http://localhost:5174 / :8001 |
| KV 生成 | http://localhost:5175 / :8002 |
| 表情包 | http://localhost:5176 / :8003 |

## 常用命令

```bash
pnpm dev           # 启动所有前端
pnpm build         # 构建所有前端
pnpm typecheck     # 类型检查
pnpm lint          # ESLint 检查
pnpm format        # Prettier 格式化
pnpm test          # 运行前端测试
pytest             # 运行后端测试
ruff check .       # Python 代码检查
```

## Docker 开发

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up    # 开发模式
docker compose -f docker-compose.yml -f docker-compose.prod.yml up   # 生产模式
```
