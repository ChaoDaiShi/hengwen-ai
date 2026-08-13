# 衡文 AI 后端

衡文 AI 后端 MVP 基于 Python 3.12、FastAPI、SQLAlchemy 2、Alembic 和 uv，提供论文上传、统一解析、规则审查、任务进度事件和审查报告 API。当前实现不依赖外部 AI 服务；AI 审查通过可替换接口预留，默认实现不会发起网络请求。

## 已实现能力

- 上传 `.docx`、`.pdf`、`.md`，校验扩展名、大小及真实文件结构
- 文件随机命名存储，记录 SHA-256，不信任用户提供的路径
- DOCX、PDF、Markdown 统一解析为章节、段落、表格、图片与参考文献模型
- 18 条确定性规则：格式 6 条、结构 5 条、图表题注 4 条、参考文献 3 条
- 持久化任务、增量 SSE 事件、任务恢复、审查报告与分页列表
- 统一 camelCase 响应和错误结构，数据库异常不会向客户端暴露连接信息
- SQLite 本地开发与测试，MySQL 生产连接配置

## 快速启动

先安装 [uv](https://docs.astral.sh/uv/)，然后在本目录执行：

```powershell
uv sync
Copy-Item .env.example .env
uv run alembic upgrade head
uv run hengwen-api
# 开发时也可以使用：uv run uvicorn hengwen_api.main:app --reload
```

服务默认监听 `http://127.0.0.1:8000`：

- 健康检查：`GET /api/v1/health`
- Swagger UI：`GET /api/docs`
- OpenAPI：`GET /api/openapi.json`

应用启动前必须先执行迁移。默认 SQLite 数据库与上传文件都位于 `storage/`；该目录以及 `*.db`、`*.sqlite`、`*.sqlite3` 已被 Git 忽略，禁止提交数据库文件。

## 配置

环境变量统一使用 `HENGWEN_` 前缀，完整示例见 `.env.example`。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `HENGWEN_ENV` | `development` | `development`、`test` 或 `production` |
| `HENGWEN_HOST` | `127.0.0.1` | 服务监听地址 |
| `HENGWEN_PORT` | `8000` | 服务端口 |
| `HENGWEN_DATABASE_URL` | `sqlite:///./storage/hengwen.db` | SQLAlchemy 数据库 URL |
| `HENGWEN_STORAGE_DIR` | `./storage` | 上传文件目录 |
| `HENGWEN_MAX_FILE_SIZE_MB` | `20` | 单文件上限 |
| `HENGWEN_CORS_ORIGINS` | 本地 Vite 地址 | 逗号分隔的允许来源 |
| `HENGWEN_SSE_POLL_INTERVAL_SECONDS` | `0.25` | SSE 数据库轮询间隔 |
| `HENGWEN_SSE_KEEPALIVE_SECONDS` | `15` | SSE 心跳间隔 |
| `HENGWEN_LOG_LEVEL` | `INFO` | 日志级别 |

生产 MySQL 示例：

```dotenv
HENGWEN_ENV=production
HENGWEN_DATABASE_URL=mysql+pymysql://hengwen:<password>@<host>:3306/hengwen
```

不要把真实连接串、密码或 `.env` 提交到仓库。

## API 流程

### 1. 上传文档

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -F "file=@paper.docx"
```

成功返回 `201`，其中 `id` 是后续创建任务所需的 `documentId`。

### 2. 创建审查任务

```bash
curl -X POST http://127.0.0.1:8000/api/v1/review-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "documentId": 1,
    "settings": {
      "orgName": "示例高校",
      "standard": "本科毕业论文规范",
      "checkFormat": true,
      "checkCitation": true,
      "checkPlagiarism": false,
      "autoReport": true
    }
  }'
```

成功返回 `202`。任务在同一服务进程的后台执行，状态和事件均持久化。服务重启时，遗留的未完成任务会被安全标记为失败并写入终态事件，客户端可据此重新提交；MVP 不自动续跑中断任务。

### 3. 查询状态与订阅事件

```bash
curl http://127.0.0.1:8000/api/v1/review-tasks/<taskId>
curl -N http://127.0.0.1:8000/api/v1/review-tasks/<taskId>/events
```

断线重连时可通过 `Last-Event-ID` 请求头继续读取尚未消费的事件：

```bash
curl -N -H "Last-Event-ID: 12" \
  http://127.0.0.1:8000/api/v1/review-tasks/<taskId>/events
```

### 4. 获取报告

```bash
curl http://127.0.0.1:8000/api/v1/reports/<reportId>
curl "http://127.0.0.1:8000/api/v1/reports?page=1&pageSize=20"
```

报告包含字数、分数、结论以及可定位的问题列表。即使没有发现问题，只要任务成功完成，也会生成报告。

## 错误响应

所有业务错误使用统一结构：

```json
{
  "code": "INVALID_FILE_TYPE",
  "message": "仅支持 .docx / .pdf / .md 文件",
  "details": null,
  "requestId": "req_..."
}
```

`requestId` 同时写入响应头 `x-request-id`，用于关联服务日志。服务端不会记录上传正文，也不会把数据库异常文本或堆栈返回客户端。

## 数据库迁移

```powershell
# 应用现有迁移
uv run alembic upgrade head

# 检查 ORM 模型与迁移是否一致
uv run alembic check

# 开发新模型变更时生成迁移，生成后必须人工审阅
uv run alembic revision --autogenerate -m "describe change"
```

首个迁移建立 `documents`、`review_tasks`、`review_issues`、`task_events` 四张表。不要通过复制本地 SQLite 文件共享数据或迁移结构。

## 开发检查

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
```

测试数据库由 pytest 在临时目录动态创建，测试结束后不会留下或提交 SQLite 文件。

## 目录结构

```text
src/hengwen_api/
├── api/v1/              # HTTP 路由
├── core/                # 配置、日志、错误码
├── db/                  # SQLAlchemy 引擎与会话
├── document_engine/     # 统一文档模型、解析器、规则和评分
├── models/              # ORM 模型
├── repositories/        # 数据访问层
├── schemas/             # API DTO
├── services/            # 上传与任务编排
├── workers/             # 审查执行与恢复
└── sse.py               # 持久化事件流
```

MVP 的后台任务运行在 API 进程内，适合单实例部署；多实例或更高吞吐量场景应将执行器迁移到独立队列系统。查重能力当前只保留配置字段，未接入外部查重服务。
