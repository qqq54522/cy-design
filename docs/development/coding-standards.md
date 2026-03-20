# 编码规范

## 前端

- **TypeScript**：严格模式，禁止 `any`，路径别名 `@/` → `src/`，`@shared/` → 共享层
- **React**：组件 PascalCase，hooks camelCase，Store 按业务域拆分
- **样式**：Tailwind CSS utility classes，避免内联 style
- **API**：统一封装 HTTP 客户端，错误处理走 AppError 模型

## 后端

- **Python 3.11+**：所有函数签名必须有类型注解
- **FastAPI 分层**：路由层 `api/` → 服务层 `services/` → 模型层 `models/` → 核心层 `core/`
- **异常**：继承 `shared.backend.core.exceptions.AppError`
- **日志**：使用 `structlog`，关键操作必须记录日志

## 提交规范

```
<type>(<scope>): <subject>
```

- **type**: feat / fix / refactor / docs / style / test / chore
- **scope**: platform / content / kv / emoji / shared / infra
