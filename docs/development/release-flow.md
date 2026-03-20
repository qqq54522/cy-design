# 发布流程

> TODO: 待补充完整发布流程文档

## 概述

本文档描述灵桥 Creative Hub 的版本发布流程。

## 版本号规范

- 遵循 [Semantic Versioning](https://semver.org/) 规范
- 格式：`MAJOR.MINOR.PATCH`

## 发布步骤

1. **代码冻结** — 确认所有功能已合并到 `main` 分支
2. **版本号更新** — 更新 `package.json` 中的版本号
3. **变更日志** — 更新 CHANGELOG
4. **构建验证** — 执行完整的 lint / typecheck / test / build
5. **Docker 镜像构建** — `docker compose -f docker-compose.yml -f docker-compose.prod.yml build`
6. **部署** — 参考 [部署文档](../operations/deploy.md)
7. **验证** — 检查各模块健康检查端点

## 回滚策略

- Docker 镜像打 tag 后保留历史版本
- 回滚时切换到上一个稳定 tag
