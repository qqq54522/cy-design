# 灵桥 Creative Hub — 问题与优化清单

> 基于 2026-03-21 全量代码审查 + 架构评估生成
>
> 本文档为项目当前问题的**唯一跟踪入口**。`PROJECT-MATURITY-TASKS.md` 保留为长期路线图。

---

## 一、总体评价

| 维度 | 评分 | 说明 |
|------|------|------|
| 目录结构 | ★★★★☆ | monorepo + 模块化清晰，shared 层已建立 |
| 依赖管理 | ★★★★☆ | pnpm workspace 统一，版本对齐 |
| 代码规范 | ★★★★☆ | ESLint / Prettier / Husky / lint-staged 已就位 |
| 共享复用 | ★★★★☆ | 前后端共享层已提取，大量重复代码已修复 |
| 模块可扩展性 | ★★★★★ | modules.json 注册机制 + 模块接入协议，非常易扩展 |
| 测试覆盖 | ★★☆☆☆ | 仅有 smoke test，业务逻辑测试缺失 |
| CI/CD | ★☆☆☆☆ | 完全缺失 |
| 文档完整度 | ★★★★☆ | 架构/开发/运维文档框架已搭建，部分内容待补充 |

---

## 二、架构亮点（做得好的地方）

1. **Monorepo 管理规范** — pnpm workspace + 统一脚本 + 版本对齐
2. **模块化设计清晰** — Hub Shell + 3 个独立模块 + 共享层，职责边界明确
3. **模块注册机制** — `config/modules.json` 集中管理模块元信息，新模块接入成本极低
4. **TypeScript 配置统一** — `tsconfig.base.json` 继承体系 + 统一 alias
5. **Docker 多阶段构建** — dev / prod 分离，base + override 的 compose 结构
6. **代码质量工具链** — ESLint flat config + Prettier + Husky + lint-staged + Ruff
7. **文档框架已搭建** — `docs/` 分层（architecture / development / operations）
8. **前后端共享层已建立** — 前端 `@lingqiao/shared`（组件/hooks/API/类型）+ 后端 `shared/backend/`（AIRouter/异常/日志/存储）

---

## 三、已解决的历史问题（归档）

> 以下问题已在 2026-03-21 修复，保留记录供参考。

<details>
<summary>点击展开已解决问题列表（12 项）</summary>

| # | 问题 | 修复日期 |
|---|------|----------|
| 1 | 后端 AI Router 跨模块重复 → 提取到 `shared/backend/core/ai_router.py` | 2026-03-21 |
| 2 | 环境变量命名 typo（NANOBANANO → NANOBANANA） | 2026-03-21 |
| 3 | Docker Compose 缺少 env_file | 2026-03-21 |
| 4 | 前端 API Client 重复且不一致 → 提取 `createApiClient()` | 2026-03-21 |
| 5 | 前端 Layout / Sidebar 模式重复 → 提取 `ModuleLayout` / `ModuleSidebar` | 2026-03-21 |
| 6 | 后端 Storage 模式不统一 → 提取 `shared/backend/core/storage.py` | 2026-03-21 |
| 7 | 后端异常类各自定义 → 扩充 `shared/backend/core/exceptions.py` | 2026-03-21 |
| 8 | 根 `.env.example` 与模块 env 不对齐 → 已更新 | 2026-03-21 |
| 9 | 缺失的文档（release-flow / monitoring）→ 已创建占位 | 2026-03-21 |
| 10 | 启动脚本 npm vs pnpm 不一致 → 已统一为 pnpm | 2026-03-21 |
| 11 | 前端 CSS 主题变量重复 → 已统一 | 2026-03-21 |
| 12 | Vite 配置重复 → 提取 `createViteConfig()` 工厂函数 | 2026-03-21 |

</details>

---

## 四、当前待解决问题

### 🔴 P0 — 高优先级（建议立即处理）

---

#### P0-1. 无 CI/CD 流水线

- **现状**：没有 `.github/workflows/` 或任何 CI 配置
- **风险**：代码质量无法自动保障，合并错误代码无门禁，多人协作时极易引入回归 bug
- **影响范围**：全项目
- **预计耗时**：2-3 小时

**建议方案**：创建最小 GitHub Actions 流水线

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck
      - run: pnpm test
      - run: pnpm build

  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff pytest
      - run: ruff check .
      - run: cd platform_api && pip install -r requirements.txt && pytest
```

**验收标准**：
- [ ] 每次 push / PR 自动运行 lint → typecheck → test → build
- [ ] 前后端检查均覆盖
- [ ] 失败时阻止合并

---

#### P0-2. 根目录缺少 README.md

- **现状**：项目根目录没有 `README.md`，仅 `docs/README.md` 作为文档索引
- **风险**：新人/协作者打开仓库后无法快速了解项目全貌
- **影响范围**：根目录
- **预计耗时**：30 分钟

**建议内容**：

```markdown
# 灵桥 Creative Hub

> AIGC 创意资产一站式平台

## 项目简介
## 技术栈
## 快速开始
## 项目结构
## 模块列表
## 文档入口
## 贡献指南
```

**验收标准**：
- [ ] 根目录存在 `README.md`
- [ ] 包含项目简介、快速启动步骤、架构概览图
- [ ] 新人可在 5 分钟内了解项目全貌

---

#### P0-3. 缺少模块脚手架生成器

- **现状**：新建模块需要手动复制目录、修改配置、注册到 `modules.json`，步骤多且容易遗漏
- **风险**：新模块接入不规范，目录结构/配置不一致
- **影响范围**：`scripts/`、`config/`
- **预计耗时**：2-3 小时

**建议方案**：创建 `scripts/create-module.ps1` 脚手架脚本

```
用法：.\scripts\create-module.ps1 -Key "poster" -Name "AI 海报" -FrontendPort 5177 -BackendPort 8004

自动完成：
1. 创建标准目录结构（frontend/ + backend/ + data/ + docs/）
2. 生成前端脚手架（package.json、vite.config.ts、tsconfig.json、App.tsx）
3. 生成后端脚手架（main.py、config.py、requirements.txt、Dockerfile）
4. 注册到 config/modules.json
5. 添加到 pnpm-workspace.yaml
6. 添加到 docker-compose.yml / docker-compose.dev.yml / docker-compose.prod.yml
7. 生成 .env.example
```

**验收标准**：
- [ ] 一条命令即可创建完整的新模块骨架
- [ ] 生成的模块可直接启动运行
- [ ] 自动遵守 `module-contract.md` 中的所有约定

---

### 🟡 P1 — 中优先级（1-2 周内处理）

---

#### P1-1. 测试覆盖严重不足

- **现状**：
  - 前端：仅 Hub 和各模块有 smoke test（仅验证渲染不报错）
  - 后端：仅 `platform_api` 有 pytest 健康检查测试
  - 三个业务模块的核心业务逻辑（AI 调用、项目 CRUD、导出）**零测试**
- **风险**：重构或新增功能时无法确认是否引入回归 bug
- **影响范围**：全项目
- **预计耗时**：持续投入

**建议分步推进**：

| 阶段 | 目标 | 具体内容 |
|------|------|----------|
| **第一步** | 后端核心测试 | 为 3 个模块后端接入 pytest，覆盖健康检查 + 项目 CRUD |
| **第二步** | AI 调用测试 | 测试 `AIRouter` 的 fallback/重试/mock 模式 |
| **第三步** | 前端组件测试 | 为 `@lingqiao/shared` 共享组件补充 Vitest 测试 |
| **第四步** | 前端页面测试 | 为各模块关键页面补充 smoke test + 交互测试 |
| **第五步** | 导出流程测试 | 覆盖各模块的导出/下载关键路径 |

**首批必测对象**：
- [ ] `shared/backend/core/ai_router.py` — AIRouter fallback 逻辑
- [ ] 各模块 `/health` 端点
- [ ] 各模块项目/任务 CRUD 接口
- [ ] `@lingqiao/shared` 的 `createApiClient` 错误处理
- [ ] `ModuleLayout` / `ModuleSidebar` 组件渲染

**验收标准**：
- [ ] 每个后端模块至少有 5 个核心接口测试
- [ ] 共享层组件和工具函数有单元测试
- [ ] `pnpm test` 可一键运行所有测试

---

#### P1-2. Hub 前端未使用 workspace 依赖

- **现状**：Hub 前端（`frontend/`）通过 `@shared` 路径别名引用共享代码，而非 pnpm workspace 的 `@lingqiao/shared: workspace:*`
- **风险**：与其他 3 个模块的依赖方式不一致，构建行为可能不同
- **影响范围**：`frontend/package.json`、`frontend/tsconfig.json`、`frontend/vite.config.ts`
- **预计耗时**：1 小时

**建议方案**：

```diff
# frontend/package.json
  "dependencies": {
+   "@lingqiao/shared": "workspace:*",
    ...
  }

# frontend/tsconfig.app.json — 移除 @shared/* 别名，改用 @lingqiao/shared
# frontend/vite.config.ts — 移除 @shared alias
```

**验收标准**：
- [ ] Hub 前端通过 `import { xxx } from '@lingqiao/shared'` 引用共享代码
- [ ] 与其他 3 个模块的引用方式完全一致
- [ ] `pnpm build` 构建通过

---

#### P1-3. 共享组件 API 风格未约定

- **现状**：`@lingqiao/shared` 已有 5 个组件（ConfirmDialog、ModuleLayout、ModuleSidebar、PlatformBridge、Spinner），但缺少统一的 API 设计规范
- **风险**：后续新增共享组件时，props 命名、回调风格、样式方案可能不一致
- **影响范围**：`shared/frontend/components/`
- **预计耗时**：1 小时

**建议约定**：

```markdown
## 共享组件 API 规范

### 命名
- Props 接口：`XxxProps`（如 `SpinnerProps`、`ConfirmDialogProps`）
- 回调函数：`onXxx`（如 `onConfirm`、`onCancel`、`onChange`）
- 布尔属性：`isXxx` 或 `hasXxx`（如 `isOpen`、`isLoading`、`hasError`）

### 样式
- 使用 Tailwind CSS，不使用 CSS Modules 或 styled-components
- 支持 `className` prop 进行样式扩展
- 使用 Tailwind 主题变量（`--color-primary` 等）保持一致性

### 导出
- 每个组件一个文件夹：`components/Xxx/index.tsx`
- 统一从 `components/index.ts` 导出
- 类型单独导出

### 文档
- 每个组件在 JSDoc 中说明用途和基本用法
```

**验收标准**：
- [ ] 在 `shared/frontend/` 中创建 `COMPONENT-GUIDE.md`
- [ ] 现有 5 个组件符合约定
- [ ] 新增组件时有规范可参考

---

#### P1-4. 统一 API 契约待完善

- **现状**：
  - 成功/失败/分页响应格式已定义（`shared/backend/core/responses.py`）
  - 但缺少：统一错误码分层、统一任务状态结构、统一项目实体基础字段
- **风险**：各模块的错误码、任务状态定义不一致，前端需要为不同模块写多套解析逻辑
- **影响范围**：`shared/backend/`、`shared/frontend/types/`
- **预计耗时**：2-3 小时

**建议方案**：

```python
# shared/backend/core/error_codes.py

class ErrorCode:
    # 平台级
    PLATFORM_MODULE_NOT_FOUND = "PLATFORM_001"
    PLATFORM_SERVICE_UNAVAILABLE = "PLATFORM_002"

    # 通用业务级
    RESOURCE_NOT_FOUND = "BIZ_001"
    VALIDATION_FAILED = "BIZ_002"
    TASK_FAILED = "BIZ_003"

    # AI 调用级
    AI_MODEL_UNAVAILABLE = "AI_001"
    AI_QUOTA_EXCEEDED = "AI_002"
    AI_TIMEOUT = "AI_003"

    # 模块前缀：CONTENT_*、KV_*、EMOJI_*
```

```python
# shared/backend/core/models.py

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseProject(BaseModel):
    id: str
    name: str
    module: str
    created_at: datetime
    updated_at: datetime
    status: str
```

**验收标准**：
- [ ] 错误码有统一前缀和分层
- [ ] 任务状态枚举全平台统一
- [ ] 项目实体有统一的基础字段
- [ ] 前端可用同一套逻辑解析所有模块的响应

---

#### P1-5. 文档内容待补充

- **现状**：
  - `docs/development/release-flow.md` — 仅 TODO 占位，无实际内容
  - `docs/operations/monitoring.md` — 仅 TODO 占位，无实际内容
  - `docs/modules/` 下缺少各模块的独立文档
  - `docs/README.md` 中引用了不存在的文档链接
- **影响范围**：`docs/`
- **预计耗时**：2 小时

**需要补充的文档**：

| 文档 | 当前状态 | 需要补充的内容 |
|------|----------|----------------|
| `docs/development/release-flow.md` | TODO 占位 | 版本号规范、发布步骤、回滚策略 |
| `docs/operations/monitoring.md` | TODO 占位 | 健康检查端点、日志查看、常见问题排查 |
| `docs/modules/content-marketing.md` | 不存在 | 素材抓取模块架构、API 列表、配置说明 |
| `docs/modules/kv-generator.md` | 不存在 | KV 生成模块架构、API 列表、配置说明 |
| `docs/modules/emoji-generator.md` | 不存在 | 表情包模块架构、API 列表、配置说明 |
| `docs/README.md` | 存在过时链接 | 清理无效链接，更新文档索引 |

**验收标准**：
- [ ] 所有被引用的文档都有实际内容
- [ ] 每个业务模块有独立的架构说明文档
- [ ] `docs/README.md` 中无死链接

---

### 🟢 P2 — 低优先级（长期优化）

---

#### P2-1. 中文目录名存在跨平台风险

- **现状**：三个业务模块使用中文目录名（`素材抓取/`、`KV生成/`、`表情包/`）
- **风险**：
  - Linux CI 环境可能出现编码问题
  - Docker 构建时路径处理可能异常
  - Git 在不同操作系统间同步时可能出现乱码
  - 部分工具链对中文路径支持不佳
- **影响范围**：全项目目录结构
- **预计耗时**：3-4 小时（含所有配置文件更新）

**建议方案**：

```
当前                          →  建议
素材抓取/content-marketing/   →  modules/content-marketing/
KV生成/                       →  modules/kv-generator/
表情包/                       →  modules/emoji-generator/
```

同时引入 `modules/` 聚合目录，让结构更清晰：

```
灵桥design/
├── modules/
│   ├── content-marketing/    # 素材抓取
│   ├── kv-generator/         # KV 生成
│   └── emoji-generator/      # 表情包
├── frontend/                 # Hub 壳层
├── platform_api/             # 平台 API
├── shared/                   # 共享层
└── config/                   # 配置中心
```

**需要同步更新的文件**：
- [ ] `config/modules.json` — 所有路径引用
- [ ] `pnpm-workspace.yaml` — 工作区路径
- [ ] `docker-compose.yml` / `dev.yml` / `prod.yml` — 构建上下文和挂载路径
- [ ] `scripts/*.ps1` — 脚本中的路径引用
- [ ] `start.ps1` / `start.bat` — 启动脚本
- [ ] `docs/` — 文档中的路径引用
- [ ] `.gitignore` — 忽略规则
- [ ] 各模块内部的相对路径引用

**验收标准**：
- [ ] 所有目录名为纯英文
- [ ] 所有配置文件中的路径引用已更新
- [ ] `pnpm install` / `pnpm build` / `pnpm test` 正常通过
- [ ] Docker 构建正常通过

---

#### P2-2. 缺少 .cursor/rules/ 项目规则

- **现状**：项目中没有 `.cursor/rules/` 目录，AI 辅助开发时缺乏项目上下文
- **风险**：AI 生成的代码可能不符合项目规范，需要反复修正
- **影响范围**：开发体验
- **预计耗时**：1 小时

**建议创建的规则文件**：

```
.cursor/rules/
├── project-overview.mdc      # 项目架构概览、模块列表、技术栈
├── frontend-conventions.mdc  # 前端编码规范、组件风格、状态管理
├── backend-conventions.mdc   # 后端编码规范、API 设计、异常处理
├── new-module-guide.mdc      # 新模块创建指南
└── shared-layer.mdc          # 共享层使用指南
```

**验收标准**：
- [ ] AI 辅助开发时能自动获取项目上下文
- [ ] 生成的代码符合项目规范

---

#### P2-3. 缺少 PR / Issue 模板

- **现状**：没有 `.github/PULL_REQUEST_TEMPLATE.md` 和 `.github/ISSUE_TEMPLATE/`
- **风险**：多人协作时 PR 和 Issue 描述不规范，缺少必要信息
- **影响范围**：`.github/`
- **预计耗时**：30 分钟

**建议方案**：

```markdown
<!-- .github/PULL_REQUEST_TEMPLATE.md -->
## 变更说明
## 影响模块
- [ ] Hub 前端
- [ ] 平台 API
- [ ] 素材抓取
- [ ] KV 生成
- [ ] 表情包
- [ ] 共享层
## 测试情况
## 截图（如有 UI 变更）
```

**验收标准**：
- [ ] 创建 PR 时自动填充模板
- [ ] 创建 Issue 时有 Bug / Feature 两种模板

---

#### P2-4. 平台 API 缺少中间件增强

- **现状**：`platform_api/` 目前是简单的聚合层，缺少生产级中间件
- **风险**：无法追踪请求链路，模块异常可能拖垮平台
- **影响范围**：`platform_api/`
- **预计耗时**：持续投入

**建议逐步添加**：

| 中间件 | 作用 | 优先级 |
|--------|------|--------|
| 请求 ID（X-Request-ID） | 全链路追踪 | 高 |
| 请求日志 | 记录请求耗时、状态码 | 高 |
| 超时控制 | 防止模块慢响应拖垮平台 | 中 |
| 错误隔离 | 单模块异常不影响其他模块 | 中 |
| 响应缓存 | 减少重复请求 | 低 |
| 熔断/降级 | 模块不可用时返回降级数据 | 低 |

**验收标准**：
- [ ] 每个请求有唯一 ID
- [ ] 请求日志包含耗时和状态码
- [ ] 单模块异常不影响平台整体可用性

---

#### P2-5. 前端体验统一待深化

- **现状**：虽然已有 `ModuleLayout` 和 `ModuleSidebar`，但各模块在以下方面仍不统一
- **影响范围**：`shared/frontend/`、各模块前端
- **预计耗时**：持续投入

**待统一项**：

| 项目 | 当前状态 | 建议 |
|------|----------|------|
| 加载态 | 各模块自行实现 | 提供统一 `<LoadingState>` 组件 |
| 错误态 | 各模块自行实现 | 提供统一 `<ErrorState>` 组件 |
| 空状态 | 各模块自行实现 | 提供统一 `<EmptyState>` 组件 |
| Toast 通知 | 各模块自行实现 | 提供统一 Toast 方案 |
| 表格组件 | 各模块自行实现 | 提供统一 `<DataTable>` 组件 |
| 表单组件 | 各模块自行实现 | 提供统一表单组件集 |
| 响应式规则 | 部分模块有移动端适配 | 统一断点和响应式策略 |

**验收标准**：
- [ ] 不同模块切换时无明显"像不同系统"的割裂感
- [ ] 关键交互组件复用率 > 80%

---

#### P2-6. E2E 测试体系

- **现状**：无任何端到端测试
- **风险**：模块间集成、iframe 嵌入、跨模块导航等场景无法自动验证
- **影响范围**：全项目
- **预计耗时**：持续投入

**建议方案**：

```
技术选型：Playwright
覆盖范围（按优先级）：
1. Hub 首页加载 + 模块导航
2. 各模块 iframe 嵌入正常
3. 素材抓取：热搜列表 → 创作 → 导出
4. KV 生成：新建活动 → 生成 → 导出
5. 表情包：上传 → 生成 → 下载
```

**验收标准**：
- [ ] 关键用户路径有 E2E 覆盖
- [ ] CI 中可自动运行 E2E 测试

---

#### P2-7. 数据层升级

- **现状**：所有模块使用文件系统（JSON 文件）存储数据
- **风险**：并发写入可能丢数据，查询能力有限，无法做复杂筛选和聚合
- **影响范围**：全项目后端
- **预计耗时**：大型重构

**建议路径**：

```
阶段 1：保持文件存储，但统一存储接口（已完成 BaseStorage）
阶段 2：引入 SQLite 作为元数据存储，文件资产保持文件系统
阶段 3：视规模决定是否迁移到 PostgreSQL
```

**验收标准**：
- [ ] 存储层有统一抽象，切换实现不影响业务代码
- [ ] 元数据支持查询、筛选、排序

---

## 五、建议执行顺序

### 第一批（本周）— 低成本高收益

| # | 任务 | 预计耗时 | 影响范围 |
|---|------|----------|----------|
| P0-2 | 创建根目录 README.md | 30 分钟 | 根目录 |
| P1-2 | Hub 前端改用 workspace 依赖 | 1 小时 | frontend/ |
| P1-3 | 制定共享组件 API 规范 | 1 小时 | shared/frontend/ |
| P2-2 | 创建 .cursor/rules/ 项目规则 | 1 小时 | .cursor/ |

### 第二批（下周）— 质量保障基础

| # | 任务 | 预计耗时 | 影响范围 |
|---|------|----------|----------|
| P0-1 | 建立 CI/CD 流水线 | 2-3 小时 | 全项目 |
| P0-3 | 创建模块脚手架生成器 | 2-3 小时 | scripts/ |
| P1-4 | 完善统一 API 契约 | 2-3 小时 | shared/ |
| P2-3 | 创建 PR / Issue 模板 | 30 分钟 | .github/ |

### 第三批（两周内）— 测试与文档

| # | 任务 | 预计耗时 | 影响范围 |
|---|------|----------|----------|
| P1-1 | 补充核心测试（后端优先） | 持续 | 全项目 |
| P1-5 | 补充文档内容 | 2 小时 | docs/ |
| P2-4 | 平台 API 添加请求 ID + 日志 | 2 小时 | platform_api/ |

### 第四批（长期）— 架构演进

| # | 任务 | 预计耗时 | 影响范围 |
|---|------|----------|----------|
| P2-1 | 中文目录名迁移 | 3-4 小时 | 全项目 |
| P2-5 | 前端体验统一深化 | 持续 | shared + 各前端 |
| P2-6 | E2E 测试体系 | 持续 | 全项目 |
| P2-7 | 数据层升级 | 大型重构 | 全项目后端 |

---

## 六、新模块接入速查

> 当你需要添加新功能模块时，按以下步骤操作：

### 快速接入（当前方式，约 30 分钟）

1. **创建目录**：按 `docs/architecture/module-contract.md` 约定创建 `模块名/frontend/` + `模块名/backend/` + `模块名/data/`
2. **前端脚手架**：复制任意模块的前端，修改 `package.json`（名称）、`vite.config.ts`（端口）
3. **后端脚手架**：复制任意模块的后端，修改 `config.py`（端口）、`main.py`（模块名）
4. **注册模块**：在 `config/modules.json` 添加模块配置
5. **注册工作区**：在 `pnpm-workspace.yaml` 添加前端路径
6. **注册容器**：在 `docker-compose*.yml` 添加服务定义
7. **安装依赖**：根目录执行 `pnpm install`
8. **启动验证**：`pnpm dev` 或 `.\start.ps1`

### 关键检查清单

- [ ] 后端实现了 `GET /health` 端点
- [ ] API 响应格式遵守 `shared/backend/core/responses.py`
- [ ] 异常继承 `shared/backend/core/exceptions.py`
- [ ] 前端使用 `@lingqiao/shared` 的 `ModuleLayout` + `createApiClient`
- [ ] 前端 `vite.config.ts` 使用 `createViteConfig()` 工厂函数
- [ ] 端口号不与现有模块冲突

---

## 七、文档维护说明

- 本文档为项目当前问题的**唯一跟踪入口**
- 问题解决后将条目移入"已解决的历史问题"折叠区，注明日期
- 新发现的问题追加到对应优先级分类下，编号递增
- 每月审查一次，更新优先级和状态
- 长期路线图请参考 `PROJECT-MATURITY-TASKS.md`
