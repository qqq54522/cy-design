# 部署说明

## Docker 部署

```bash
# 开发模式（热重载）
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 生产模式
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 停止
docker compose down
```

## 环境变量

所有环境变量在 `.env.example` 中有完整模板。关键配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PLATFORM_PORT` | 平台 API 端口 | 8100 |
| `HUB_FRONTEND_PORT` | Hub 前端端口 | 5180 |
| `OPENAI_API_KEY` | OpenAI API Key | — |
| `GEMINI_API_KEY` | Gemini API Key | — |
| `DATA_ROOT` | 数据存储根目录 | ./data |

## 健康检查

```bash
curl http://localhost:8100/health   # 平台
curl http://localhost:8001/health   # 素材抓取
curl http://localhost:8002/health   # KV 生成
curl http://localhost:8003/health   # 表情包
```
