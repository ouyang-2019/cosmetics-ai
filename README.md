# 化妆品AI智能平台

> 化妆品行业垂直AI平台，集成法规检索、文档审核、文案合规、知识库问答四大核心能力。

## 项目概述

本平台参考智合AI（法律行业AI平台）的产品架构，为化妆品生产制造行业定制开发。帮助化妆品企业提升法规合规效率和知识管理水平。

### 核心功能

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| 法规智能检索 | 化妆品法规语义检索与AI智能摘要，支持溯源引用 | ✅ 前端完成 |
| 体系文件审核 | GMP/SOP等体系文件的AI辅助审核，生成审核报告 | ✅ 前端完成 |
| 文案合规工作台 | 产品文案合规审核 + 合规文案生成，双模式工作台 | ✅ 前端完成 |
| 知识库问答 | 企业知识库多轮对话问答，支持溯源引用 | ✅ 前端完成 |
| 用户认证 | JWT认证，支持注册/登录，部门/角色管理 | ✅ 前后端完成 |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户层 (Web Browser)                       │
│  ┌──────────┬──────────┬───────────┬──────────┐             │
│  │ 法规检索  │ 文档审核  │ 文案工作台 │ 知识问答  │             │
│  └──────────┴──────────┴───────────┴──────────┘             │
└────────────────────────┬────────────────────────────────────��
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   API 网关层 (Nginx)                          │
└──────┬─────────────────┬─────────────────┬──────────────────┘
       │                 │                 │
┌──────▼──────┐  ┌───────▼───────┐  ┌──────▼──────┐
│  RAGFlow    │  │   Dify Cloud  │  │  FastAPI    │
│  (远程部署)  │  │  (官方云端)    │  │  (本机)     │
│             │  │               │  │             │
│ 文档解析     │  │ 工作流编排     │  │ 用户认证    │
│ 向量检索     │  │ LLM调用管理   │  │ 权限控制    │
│ 溯源引用     │  │ 对话应用      │  │ 代理转发    │
└──────┬──────┘  └───────┬───────┘  └──────┬──────┘
       │                 │                 │
┌──────▼─────────────────▼─────────────────▼──────────────────┐
│                      基础设施层                               │
│  MySQL 8.0 │ Redis 7 │ MinIO │ Docker Compose                │
└─────────────────────────────────────────────────────────────┘
```

### 部署方案（方案二：分布式）

| 组件 | 部署位置 | 说明 |
|------|---------|------|
| FastAPI 后端 + Vue 前端 | 本机 | 业务核心 |
| MySQL + Redis + MinIO | 本机 | 基础设施 |
| RAGFlow + Elasticsearch | 远程机器 | 知识库引擎，需较多内存 |
| Dify | 官方云端 (cloud.dify.ai) | 工作流编排，免运维 |

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus + Vite + Pinia + Vue Router 4 |
| 后端 | Python FastAPI + SQLAlchemy + Pydantic |
| AI知识库 | RAGFlow（文档解析、向量存储、混合检索） |
| AI工作流 | Dify Cloud（工作流编排、LLM调用） |
| LLM | DeepSeek API |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 文件存储 | MinIO |
| 容器化 | Docker Compose |
| 反向代理 | Nginx |

---

## 项目结构

```
cosmetics-ai/
├── docker-compose.yml              # Docker 编排（MySQL/Redis/MinIO/后端/前端/Nginx）
├── .env                            # 环境变量（RAGFlow/Dify/JWT/数据库配置）
├── .gitignore
├── nginx/
│   └── nginx.conf                  # Nginx 反向代理配置
├── backend/                        # FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt            # Python 依赖（16 packages）
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口，注册路由，CORS
│   │   ├── config.py               # Pydantic Settings 配置管理
│   │   ├── database.py             # SQLAlchemy 连接与会话
│   │   ├── models/
│   │   │   └── user.py             # 用户模型（username/email/role/department）
│   │   ├── schemas/
│   │   │   ├── user.py             # 用户 Pydantic Schema
│   │   │   ├── knowledge.py        # 知识库检索 Schema
│   │   │   └── workflow.py         # 工作流 Schema
│   │   ├── services/
│   │   │   ├── auth.py             # JWT 认证服务（bcrypt 密码哈希）
│   │   │   ├── ragflow.py          # RAGFlow HTTP 客户端
│   │   │   └── dify.py             # Dify HTTP 客户端（工作流+对话）
│   │   └── routers/
│   │       ├── auth.py             # POST /api/auth/register, /login
│   │       ├── knowledge.py        # POST /api/knowledge/search, GET /datasets
│   │       └── workflow.py         # POST /api/workflow/run, /chat
│   └── tests/                      # 9 个测试用例，全部通过
│       ├── test_health.py
│       ├── test_auth.py
│       ├── test_ragflow_service.py
│       └── test_dify_service.py
├── frontend/                       # Vue 3 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf                  # 前端容器内 Nginx 配置
│   └── src/
│       ├── main.ts                 # 应用入口（Element Plus + Pinia + Router）
│       ├── App.vue
│       ├── api/
│       │   ├── request.ts          # Axios 封装（拦截器/Token/错误处理）
│       │   ├── auth.ts             # 认证 API
│       │   ├── knowledge.ts        # 知识库 API
│       │   └── workflow.ts         # 工作流 API
│       ├── stores/
│       │   └── user.ts             # Pinia 用户状态
│       ├── router/
│       │   └── index.ts            # 路由（含登录守卫）
│       ├── layouts/
│       │   └── MainLayout.vue      # 主布局（侧边栏+顶栏+内容区）
│       └── views/
│           ├── Login.vue           # 登录/注册页（双Tab切换）
│           ├── RegulationSearch.vue # 法规检索页（快捷标签+历史+Markdown渲染）
│           ├── DocReview.vue       # 文档审核页（上传+进度+报告导出）
│           ├── CopyWorkbench.vue   # 文案工作台（审核/生成双模式）
│           └── KnowledgeChat.vue   # 知识问答页（多轮对话+溯源+会话管理）
└── docs/
    └── plans/
        ├── ...design.md            # 系统设计文档
        └── ...implementation.md    # 实施计划文档
```

---

## 开发进度

### Phase 1：项目基础与后端 ✅ 已完成

| 任务 | 描述 | 状态 | Commit |
|------|------|------|--------|
| Task 1 | 初始化项目目录结构 | ✅ | `32ea4cc` |
| Task 2 | Docker Compose + Nginx 配置 | ✅ | `a29acf7` |
| Task 3 | FastAPI 后端脚手架 + 健康检查 | ✅ | `1a3e2e0` |
| Task 4 | 用户认证模块（JWT 注册/登录） | ✅ | `916af54` |
| Task 5 | RAGFlow 代理服务（知识库检索） | ✅ | `916af54` |
| Task 6 | Dify 工作流代理服务 | ✅ | `916af54` |

### Phase 2：前端脚手架与页面 ✅ 已完成

| 任务 | 描述 | 状态 | Commit |
|------|------|------|--------|
| Task 7 | 初始化 Vue 3 前端项目 | ✅ | `2bb2774` |
| Task 8 | 前端路由与布局框架 | ✅ | `f2afebd` |
| Task 9 | API 层（Axios）与用户状态 | ✅ | `09efefc` |
| Task 12 | 法规检索页面完整实现 | ✅ | `415e392` |
| Task 13 | 文案工作台页面完整实现 | ✅ | `415e392` |
| Task 14 | 文档审核页面完整实现 | ✅ | `415e392` |
| Task 15 | 知识问答对话页面完整实现 | ✅ | `415e392` |
| Task 16 | 登录页面完整实现 | ✅ | `415e392` |

### Phase 3：RAGFlow 与 Dify 配置 🔲 待执行

| 任务 | 描述 | 状态 |
|------|------|------|
| Task 10 | 远程部署 RAGFlow + 创建 4 个知识库 | 🔲 |
| Task 11 | 配置 Dify Cloud + 搭建 4 个工作流 + 1 个对话应用 | 🔲 |

### Phase 4-5：联调与优化 🔲 待执行

| 任务 | 描述 | 状态 |
|------|------|------|
| Task 17 | 端到端联调测试 | 🔲 |
| Task 18 | Prompt 优化 | 🔲 |
| Task 19 | 部署文档编写 | 🔲 |

### 进度概览

```
整体进度：██████████████░░░░░░ 70%

Phase 1 后端基础    ████████████████████ 100%  (6/6 tasks)
Phase 2 前端页面    ████████████████████ 100%  (8/8 tasks)
Phase 3 AI服务配置  ░░░░░░░░░░░░░░░░░░░░   0%  (0/2 tasks)
Phase 4-5 联调优化  ░░░░░░░░░░░░░░░░░░░░   0%  (0/3 tasks)
```

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- 远程 RAGFlow 服务（另一台机器）
- Dify Cloud 账号 (cloud.dify.ai)

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/ouyang-2019/cosmetics-ai.git
cd cosmetics-ai

# 2. 配置环境变量
cp .env.example .env  # 然后编辑 .env 填入实际配置

# 3. 启动后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. 启动前端
cd frontend
npm install
npm run dev

# 5. 运行测试
cd backend
pytest tests/ -v
```

### Docker 部署

```bash
docker compose up -d
```

### 关键配置项（.env）

```env
# RAGFlow 远程地址（修改为实际 IP）
RAGFLOW_URL=http://192.168.1.100:9380
RAGFLOW_API_KEY=your-ragflow-api-key

# Dify 云端
DIFY_URL=https://api.dify.ai
DIFY_API_KEY=app-your-dify-api-key

# 各工作流 API Key（在 Dify 创建工作流后获取）
DIFY_WF_REGULATION_SEARCH_KEY=  # WF1: 法规检索
DIFY_WF_DOC_REVIEW_KEY=         # WF2: 文档审核
DIFY_WF_COPY_REVIEW_KEY=        # WF3: 文案审核
DIFY_WF_COPY_GENERATE_KEY=      # WF4: 文案生成
DIFY_CHAT_APP_KEY=               # APP1: 知识问答
```

---

## 下一步计划

1. **部署 RAGFlow**：在远程机器部署，创建 4 个知识库（法规、体系文件、文案、企业知识），上传化妆品法规文档
2. **配置 Dify Cloud**：创建 4 个工作流（法规检索、文档审核、文案审核、文案生成）+ 1 个知识问答对话应用
3. **端到端联调**：前端 → 后端 → Dify → RAGFlow 全链路测试
4. **Prompt 优化**：根据测试结果调优各工作流的 LLM Prompt

---

## 知识库设计（RAGFlow）

| 知识库 | 用途 | 数据来源 |
|--------|------|---------|
| KB1 法规知识库 | 化妆品法规条文检索 | 《化妆品监督管理条例》《安全技术规范》等 |
| KB2 体系文件库 | 企业体系文件审核参考 | GMP文件、质量手册、SOP |
| KB3 产品文案库 | 合规文案生成参考 | 已审核通过的合规文案 |
| KB4 企业知识库 | 员工知识问答 | 培训资料、FAQ、流程说明 |

## Dify 工作流设计

| 编号 | 名称 | 类型 | 流程 |
|------|------|------|------|
| WF1 | 法规检索 | Workflow | 查询改写 → RAGFlow检索 → LLM摘要+溯源 |
| WF2 | 文档审核 | Workflow | 文档解析 → 模板对比 → 法规检查 → 审核报告 |
| WF3 | 文案审核 | Workflow | 功效宣称检查 + 禁用词检查 + 法规检查 → 风险报告 |
| WF4 | 文案生成 | Workflow | 参考检索 → 法规约束 → AI生成 → 合规自检 |
| APP1 | 知识问答 | Chatbot | 基于KB4的多轮对话 |

---

## License

MIT
