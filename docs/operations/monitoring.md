# 监控方案

> TODO: 待补充完整监控方案文档

## 概述

本文档描述灵桥 Creative Hub 的监控与告警方案。

## 健康检查

各后端模块均提供 `/health` 端点：

| 模块 | 端口 | 健康检查路径 |
|------|------|-------------|
| Platform API | 8100 | `/health` |
| 素材抓取 | 8001 | `/health` |
| KV 生成 | 8002 | `/health` |
| 表情包 | 8003 | `/health` |

## 日志

- 后端日志输出到 stdout/stderr，由 Docker 收集
- 日志级别通过 `LOG_LEVEL` 环境变量控制

## 指标监控

> TODO: 接入 Prometheus / Grafana 或其他监控方案

## 告警规则

> TODO: 定义告警阈值和通知渠道
