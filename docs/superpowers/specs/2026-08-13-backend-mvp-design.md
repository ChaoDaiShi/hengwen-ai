# 衡文 AI 后端 MVP 设计

## 1. 背景与仓库现状

衡文当前由 `hengwen-web/` React 前端和 `hengwen-api/` Python 后端脚手架组成。前端已经定义上传入口、分析进度、报告详情、历史记录和设置界面，但核心数据来自 `src/api/mock.ts`、Zustand 定时器和 LocalStorage。后端仅包含 uv 初始化文件、依赖声明和 Hello World 命令，没有 FastAPI 应用、数据库、解析器、规则引擎、任务系统或测试。

本轮在当前 `feature/lsc` 分支实现可独立运行和验证的后端 MVP。除本设计文档外，产品代码改动严格限制在 `hengwen-api/`，不修改 `hengwen-web/`。React 接入作为后续工作，后端通过兼容现有 TypeScript 类型的 API 契约为接入做好准备。

## 2. 目标与验收结果

本轮交付以下真实链路：

```text
上传 DOCX / PDF / Markdown
  -> 安全校验、文件落盘和元数据持久化
  -> 创建审查任务
  -> 后台 Worker 解析文档
  -> 持久化阶段事件
  -> 确定性规则产生 Issue
  -> 计算 Score 和 Verdict
  -> 生成 Report
  -> SSE 增量读取事件
  -> 报告详情和历史分页可再次读取
```

完成标准是后端 API、迁移、测试、静态检查和本地运行验证均有当前代码的真实证据。由于本轮不修改前端，不能把“React 已脱离 mock”作为完成声明。

## 3. 已确认约束

- 当前分支为 `feature/lsc`，不创建或切换分支。
- 产品代码只修改 `hengwen-api/`，不修改 React 前端。
- Python 版本为 3.12，优先使用现有依赖；PDF 文本提取允许通过 `uv add pypdf` 增加 `pypdf`。
- 生产数据库通过 `HENGWEN_DATABASE_URL` 使用 MySQL；本地开发和测试允许使用 SQLite。
- SQLite 只作为运行时或测试依赖，任何 `.db`、`.sqlite`、`.sqlite3` 文件均不得提交。
- 测试数据库位于 pytest 临时目录；可选本地数据库位于已忽略的 `hengwen-api/storage/`。
- 数据库结构由 Alembic 迁移管理，应用启动不调用 `Base.metadata.create_all()` 代替正式迁移。
- 不伪造查重、AI 审查或 PDF 版式能力。
- API 输出使用 camelCase，Python 内部使用 snake_case。

## 4. 方案选择

### 4.1 采用方案：分层单体和 FastAPI BackgroundTasks

应用采用单进程分层单体：Router 负责 HTTP 契约，Service 负责编排，Repository 负责持久化，DocumentEngine 负责解析和规则，ReviewWorker 负责后台执行，TaskEventEmitter 负责持久事件。FastAPI BackgroundTasks 在响应完成后运行 Worker。

该方案依赖少、边界清楚，符合 MVP 不引入 Redis、Celery、RabbitMQ 或 Kafka 的限制。未来迁移独立 Worker 时，可保留 DocumentEngine、Service、事件模型、报告 Schema 和 API 契约。

### 4.2 未采用方案

- 应用内线程池调度器：并发和取消控制较强，但需要额外处理线程安全、生命周期和恢复语义，首版成本过高。
- 独立 Worker 与消息队列：扩展性更好，但引入附件明确排除的基础设施。

## 5. 总体架构

```text
FastAPI Router
    |
DocumentService / ReviewService
    |
Repository --------------------> SQLAlchemy / MySQL or SQLite
    |                                      ^
DocumentEngine                    TaskEventEmitter
    |                                      ^
ReviewWorker -----------------------------+
                                           |
                                     SSE 增量读取
```

### 5.1 API 层

负责请求校验、依赖注入、响应 Schema、状态码和异常映射。Router 不解析文档、不直接拼 SQL、不执行长任务。

### 5.2 Service 层

`DocumentService` 编排上传校验、文件保存和元数据持久化。`ReviewService` 校验任务创建条件、保存设置、创建公开 ID 并提交 Worker。Service 不依赖 FastAPI Request。

### 5.3 Repository 层

封装 SQLAlchemy 2.x typed models 的读写，返回领域模型或 ORM 实体，不返回裸 SQL tuple。事务边界由 Service 或 Worker 明确控制。

### 5.4 DocumentEngine

解析不同格式为统一 `DocumentModel`。规则只依赖该中间结构，不访问数据库或 HTTP。评分器只依赖 Issue 集合，保证确定性。

### 5.5 Worker 与 Events

`ReviewWorker` 读取文档记录、更新阶段、调用解析器和规则、保存 Issue、计算报告字段。每次阶段变化均更新任务并写入 `task_events`。事件先持久化，SSE 再读取，页面刷新不会丢失已发生事件。

## 6. 配置、启动与运行目录

使用 `pydantic-settings` 从环境变量加载至少以下配置：

```env
HENGWEN_ENV=development
HENGWEN_HOST=127.0.0.1
HENGWEN_PORT=8000
HENGWEN_DATABASE_URL=sqlite:///./storage/hengwen.db
HENGWEN_STORAGE_DIR=./storage
HENGWEN_MAX_FILE_SIZE_MB=20
HENGWEN_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

仓库提供不含真实凭据的 `.env.example`。`hengwen-api/.gitignore` 忽略 `.env`、`storage/`、`*.db`、`*.sqlite` 和 `*.sqlite3`。提交前使用 `git ls-files` 检查不存在被跟踪的 SQLite 文件。

应用入口为 `hengwen_api.main:app`，文档路由为 `/api/docs`、`/api/redoc` 和 `/api/openapi.json`。命令入口改为 `hengwen_api.main:run`，支持：

```bash
uv run hengwen-api
uv run uvicorn hengwen_api.main:app --reload
```

## 7. 数据模型与迁移

### 7.1 documents

保存数据库主键、原始文件名、服务端文件名、文件类型、大小、SHA-256、相对存储路径、状态、创建时间和软删除时间。文件二进制不进入数据库。

### 7.2 review_tasks

保存数据库主键、公开 `task_id`、公开 `report_id`、文档外键、任务状态、阶段、阶段索引、进度、四个设置开关、机构和规范设置、得分、结论、字数、开始/完成时间、错误信息和审计时间。

`task_id` 使用 `rvw_<uuid>`，`report_id` 在完成时使用 `report_<uuid>`。公开 ID 不使用可预测自增序列。

### 7.3 review_issues

保存数据库主键、公开 `public_id`、任务外键、严重度、标题、位置、摘要、原文、建议、规则代码、问题类型和创建时间。`public_id` 使用 `iss_<uuid>`。

### 7.4 task_events

保存自增事件 ID、任务外键、事件类型、阶段、阶段索引、进度、级别、消息、结构化 JSON 数据和创建时间。SSE 使用自增 ID 实现增量读取和断线续传。

### 7.5 索引与兼容性

为任务公开 ID、报告公开 ID、文档外键、状态和创建时间建立必要索引。字段类型选择同时兼容 MySQL 和 SQLite，JSON 数据使用 SQLAlchemy JSON 类型，时间统一保存带时区语义的 UTC 时间并在 API 输出 ISO 8601。

首个 Alembic revision 建立全部核心表和索引。测试使用临时 SQLite 执行 `alembic upgrade head`，不依赖真实腾讯云数据库。没有真实 MySQL 凭据时，只声明结构和方言兼容通过静态及迁移测试，不声称完成云数据库联调。

## 8. 文件上传和存储安全

`POST /api/v1/documents` 接收 multipart 字段 `file`，允许 `.docx`、`.pdf` 和 `.md`。处理顺序如下：

1. 从配置读取最大大小，流式写入临时文件并在超过限制时立即停止。
2. 只从原始文件名获取显示名称和允许后缀，不将其用于磁盘路径。
3. 生成 UUID 文件名，目标路径为 `storage/uploads/YYYY/MM/<uuid>.<ext>`。
4. 计算 SHA-256。
5. 验证后缀和真实内容：DOCX 必须为有效 ZIP/OpenXML 且包含 Word 主文档；PDF 必须以 `%PDF` 开头；Markdown 必须可作为受支持文本编码读取。
6. 原子移动到最终目录并持久化元数据。
7. 任一步失败都删除临时文件，不保留无主文件或半成品记录。

响应返回文档 ID、原始文件名、文件类型、大小、哈希、状态和创建时间。错误文件通过统一错误模型返回，不泄露服务器路径。

## 9. 统一文档模型与解析能力

### 9.1 DocumentModel

统一模型包含 metadata、sections、paragraphs、headings、tables、figures、references 和 raw_text。段落保存索引、文本、样式名、对齐、行距、Run 和 Section 信息；Run 保存文本、字体、字号、粗体、斜体和下划线。

### 9.2 DOCX

使用 `python-docx` 提取段落、Run、标题、对齐、行距、表格、Section、页边距和页眉页脚。图片关系、题注和 python-docx 未暴露的只读信息可通过 lxml/OpenXML 补充。DOCX 是首版格式规则的核心载体。

### 9.3 Markdown

解析文本、ATX/Setext 标题、标题层级、引用、章节、参考文献文本和语言内容。Markdown 不执行 Word 字号、页边距、页眉页脚或复杂分页规则。

### 9.4 PDF

通过 `pypdf` 提取文本，执行适用的结构、语言和引用规则。PDF 不声称恢复真实 Heading Style、Run 字体、原始段落样式或 Word 版式。信息不足的格式规则跳过，不猜测。

### 9.5 无效文档

空文件、损坏 DOCX、伪造 PDF、不可解码 Markdown 或没有可分析内容的文档返回 `INVALID_DOCUMENT`。解析器不执行 HTTP 或数据库操作。

## 10. 规则、AI 边界与评分

### 10.1 首版规则

实现以下 15 条核心规则：

- 格式：`FMT001` 至 `FMT006`
- 结构：`STR001` 至 `STR005`
- 图表：`CAP001` 至 `CAP004`

同时实现引用规则 `REF001` 至 `REF003`。引用规则仅在 `checkCitation=true` 且解析结果能够可靠判断时运行。格式规则仅在 `checkFormat=true` 且文档类型支持对应属性时运行。每条规则独立、可测试、可开关、具有固定 `rule_code`。

Issue 严重度只允许 `error`、`warning` 和 `info`。公开 Issue 包含 `id`、`severity`、`title`、`location`、`summary`、`original` 和 `suggestion`，可直接映射现有 React 类型。

### 10.2 AIReviewer

定义 `AIReviewer` Protocol 和 `NullAIReviewer`。未配置真实 Provider 时，规则审查正常运行，AI 阶段跳过且不生成伪 AI 内容。

### 10.3 查重

接受并持久化 `checkPlagiarism`。当该值为 true 且无真实 Provider 时，记录 `unsupported capability: plagiarism` 信息事件，不生成重复率、不生成假 Issue、不参与扣分。

### 10.4 确定性评分

评分规则固定为：

```text
初始 100
error   -8
warning -3
info    -1
最低 0
```

Verdict 规则为：没有 error 且 score 大于等于 90 时为 `pass`；score 小于 70 或严重 error 达到固定阈值时为 `fail`；其他情况为 `pending`。严重 error 阈值定义为 3，作为评分模块中的具名常量并由边界测试覆盖。

规则不使用随机数。Issue 公共 ID 虽为随机 UUID，但同一文件和同一设置的 Issue 内容、排序、得分和 Verdict 必须一致。

## 11. API 契约

### 11.1 健康检查

`GET /api/v1/health` 返回：

```json
{"status":"ok","service":"hengwen-api","version":"0.1.0"}
```

### 11.2 文档上传

`POST /api/v1/documents` 返回文档元数据，供创建任务时使用其数值 `documentId`。

### 11.3 创建任务

`POST /api/v1/review-tasks` 接受：

```json
{
  "documentId": 123,
  "settings": {
    "orgName": "",
    "standard": "本科毕业论文规范（默认）",
    "checkFormat": true,
    "checkCitation": true,
    "checkPlagiarism": false,
    "autoReport": true
  }
}
```

响应保留现有 `AnalysisTask` 所需的 `id`、`filename`、`fileType`、`stageIndex`、`progress` 和 `startedAt`。

### 11.4 查询任务

`GET /api/v1/review-tasks/{task_id}` 返回 AnalysisTask 字段并增加 `status` 和 `stage`，供刷新和 SSE 断开后恢复。

### 11.5 SSE

`GET /api/v1/review-tasks/{task_id}/events` 返回 `text/event-stream`。事件包含自增 `id`、事件名称和 camelCase JSON data，至少支持：

- `task.started`
- `stage.started`
- `task.progress`
- `issue.detected`
- `stage.completed`
- `task.completed`
- `task.failed`

Endpoint 从 `Last-Event-ID` 之后查询事件，按 ID 递增发送；无新事件约 15 秒发送 keepalive；最终事件发送后关闭。客户端断开不取消 Worker。

### 11.6 报告

`GET /api/v1/reports?page=1&pageSize=20` 返回：

```json
{"items":[],"page":1,"pageSize":20,"total":0}
```

每个 item 和 `GET /api/v1/reports/{report_id}` 均严格包含现有 React `Report` 字段：`id`、`filename`、`fileType`、`checkedAt`、`wordCount`、`score`、`verdict` 和 `issues`。

## 12. 任务状态和故障恢复

状态至少包括 `pending`、`running`、`completed` 和 `failed`。对 Web 暴露的阶段映射固定为：

```text
created      stageIndex 0  progress 0
read         stageIndex 0  progress 20
format       stageIndex 1  progress 45
citation     stageIndex 2  progress 70
suggestion   stageIndex 3  progress 90
completed    stageIndex 4  progress 100
```

Worker 失败时回滚当前不完整业务事务，随后在独立事务中保存安全的错误摘要、`failed` 状态和 `task.failed` 事件。异常堆栈只进入服务端日志。

BackgroundTasks 不提供跨进程恢复。应用启动时将遗留的 `pending` 或 `running` 任务标记为 `failed`，写入恢复事件，避免任务永久显示为运行中。用户可基于同一文档重新创建任务。本轮不实现自动重试或断点续跑。

## 13. 错误、日志和 CORS

统一业务错误至少覆盖：`INVALID_FILE_TYPE`、`FILE_TOO_LARGE`、`INVALID_DOCUMENT`、`DOCUMENT_NOT_FOUND`、`TASK_NOT_FOUND`、`REPORT_NOT_FOUND`、`INVALID_TASK_STATE`、`REVIEW_FAILED` 和 `DATABASE_ERROR`。

错误响应为：

```json
{
  "code": "INVALID_DOCUMENT",
  "message": "无法解析该文档",
  "details": null,
  "requestId": "req_<uuid>"
}
```

请求中间件生成请求 ID，并记录 request_id、task_id、document_id、stage、duration 和安全异常摘要。日志不记录完整文档正文、数据库密码、API Key、服务器绝对存储路径或 traceback 到客户端。

CORS 来源从 `HENGWEN_CORS_ORIGINS` 读取，开发默认允许 `http://localhost:5173` 和 `http://127.0.0.1:5173`，不使用 `allow_origins=["*"]` 与凭据组合。

## 14. 测试设计

测试全部使用 pytest 临时目录。测试 SQLite 数据库和上传文件随测试结束清理，不出现在 Git 工作树。DOCX 测试夹具通过 python-docx 动态生成。

- `test_health.py`：健康检查、文档入口和 OpenAPI。
- `test_upload.py`：三种允许格式、大小限制、伪造文件、路径穿越、哈希和失败清理。
- `test_docx_parser.py`：段落、Run、标题、表格、Section、空文档和损坏 DOCX。
- `test_rule_engine.py`：核心规则、引用规则、规则开关和格式适用范围。
- `test_scoring.py`：确定性扣分、最低分和 Verdict 边界。
- `test_review_task.py`：任务创建、状态转换、失败状态和不支持查重事件。
- `test_report_api.py`：报告详情、分页、camelCase 和历史读取。
- `test_sse.py`：事件顺序、最终关闭、`Last-Event-ID` 和 keepalive。
- `test_migrations.py`：临时 SQLite 执行 Alembic upgrade，并核对核心表和索引。
- 端到端测试：动态 DOCX 上传、创建任务、执行 Worker、读取事件、Issue、Report 和历史列表。

TDD 实施时，每个行为先写失败测试、确认因缺少该行为而失败，再写最小实现并确认通过。

## 15. 质量门禁和运行验证

最终执行：

```bash
cd hengwen-api
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
uv run alembic upgrade head
uv run hengwen-api
```

启动后真实请求验证：

- `GET /api/v1/health`
- `GET /api/docs`
- 上传动态生成的 DOCX
- 创建任务并读取完成事件
- 读取报告详情和历史列表

提交前检查：

```bash
git status --short
git ls-files
git diff --check
```

若 `git ls-files` 出现任何 `.db`、`.sqlite` 或 `.sqlite3` 文件，停止提交并移除跟踪；不得将数据库文件上传到远端。

## 16. 明确延后

- React 数据层和页面接入真实 API。
- 真实查重 Provider 和重复率。
- OpenAI、Claude、DeepSeek、Qwen 或其他 LLM Provider。
- 用户系统、OAuth、权限和付费。
- Redis、Celery、消息队列、微服务和多进程任务恢复。
- PDF 的高保真 Word 版式恢复。
- 腾讯云 MySQL 的真实网络连接、凭据和部署验证。

## 17. 后续前端契约提案

后续前端接入需要用真实 API 客户端替换 `src/api/mock.ts` 和 Zustand 定时器，并让历史页从分页接口加载，让分析页订阅 SSE。报告详情实体本身不需要破坏性类型修改；报告列表需要从当前本地数组适配为 `{items,page,pageSize,total}` 分页响应。该提案不在本轮实施。

## 18. 风险与处理

- BackgroundTasks 无法跨进程恢复：启动时将遗留任务失败化并明确记录，不伪造恢复能力。
- SQLite 与 MySQL 存在方言差异：避免方言专有字段，使用 Alembic 和双兼容类型；真实 MySQL 联调仍需后续环境。
- DOCX 实际样式复杂：规则基于显式样式和可验证统计，不确定时跳过，避免误报。
- PDF 文本抽取依赖文档是否包含可提取文本：扫描件或加密 PDF 无可靠文本时返回可理解错误或跳过不适用规则。
- SSE 采用数据库轮询：适合 MVP 规模，未来可替换事件传输层而保持公开协议不变。
