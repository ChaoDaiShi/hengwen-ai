# 衡文 AI 后端 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不修改 React 前端的前提下，实现可上传真实文档、持久执行规则审查、通过 SSE 恢复进度并读取兼容现有前端类型报告的 FastAPI 后端 MVP。

**Architecture:** 使用 FastAPI 分层单体，Router 只处理 HTTP 契约，Service 编排业务，Repository 封装 SQLAlchemy，DocumentEngine 负责解析和确定性规则，ReviewWorker 通过持久化 TaskEvent 驱动 SSE。MySQL 是生产目标，SQLite 仅用于 pytest 临时数据库和可选本地运行，Schema 由 Alembic 管理。

**Tech Stack:** Python 3.12、FastAPI、Pydantic v2/pydantic-settings、SQLAlchemy 2.x、Alembic、PyMySQL、python-docx、lxml、pypdf、pytest、httpx、ruff、mypy。

## Global Constraints

- 在当前 `feature/lsc` 分支执行，不创建或切换分支。
- 除设计和计划文档外，产品代码只修改 `hengwen-api/`，不修改 `hengwen-web/`。
- 不提交 `.env`、真实凭据、用户文档、运行日志、上传文件或 SQLite 数据库文件。
- `*.db`、`*.sqlite`、`*.sqlite3` 和 `storage/` 必须由 `hengwen-api/.gitignore` 忽略；每次提交前检查 `git ls-files`。
- 正式迁移只使用 Alembic；应用启动不调用 `Base.metadata.create_all()`。
- API JSON 使用 camelCase；Python 内部使用 snake_case；报告实体兼容现有 React `Report`。
- 分析阶段固定映射为 read 20、format 45、citation 70、suggestion 90、completed 100。
- 查重和 AI Provider 未配置时明确跳过，不生成伪造结果。
- PDF 只做可靠文本审查，不猜测 Word 样式或版式。
- 每个行为遵循 RED -> GREEN -> REFACTOR；没有先观察到预期失败，不写对应生产实现。

---

## File Map

### Application and API

- `hengwen-api/src/hengwen_api/main.py`: 应用工厂、lifespan、CORS、路由、CLI 启动。
- `hengwen-api/src/hengwen_api/api/dependencies.py`: Settings、Session 和 SessionFactory 请求依赖。
- `hengwen-api/src/hengwen_api/api/v1/*.py`: health、documents、review-tasks、reports 和 SSE handlers。
- `hengwen-api/src/hengwen_api/core/*.py`: 配置、异常、请求 ID 和结构化日志。
- `hengwen-api/src/hengwen_api/schemas/*.py`: camelCase 请求/响应 Schema。

### Persistence

- `hengwen-api/src/hengwen_api/db/base.py`: Declarative Base 和时间工具。
- `hengwen-api/src/hengwen_api/db/session.py`: Engine/SessionFactory 创建。
- `hengwen-api/src/hengwen_api/models/*.py`: 四张核心表的 SQLAlchemy typed models。
- `hengwen-api/src/hengwen_api/repositories/*.py`: 文档、任务、Issue、事件和报告查询。
- `hengwen-api/alembic/`: 迁移环境和首个 revision。

### Domain

- `hengwen-api/src/hengwen_api/document_engine/models.py`: 统一文档与规则 Issue 模型。
- `hengwen-api/src/hengwen_api/document_engine/*_parser.py`: DOCX、Markdown、PDF 解析。
- `hengwen-api/src/hengwen_api/document_engine/rules/*.py`: 独立格式、结构、图表、引用规则。
- `hengwen-api/src/hengwen_api/document_engine/rule_engine.py`: 规则选择和确定性聚合。
- `hengwen-api/src/hengwen_api/document_engine/scoring.py`: 得分和 Verdict。
- `hengwen-api/src/hengwen_api/ai/reviewer.py`: `AIReviewer` Protocol 和 `NullAIReviewer`。
- `hengwen-api/src/hengwen_api/events/*.py`: 持久事件模型、Repository 和 Emitter。
- `hengwen-api/src/hengwen_api/services/*.py`: 上传与任务用例。
- `hengwen-api/src/hengwen_api/workers/review_worker.py`: 后台审查状态机。

### Tests

- `hengwen-api/tests/conftest.py`: 临时 SQLite、临时 storage、app 和 TestClient fixtures。
- `hengwen-api/tests/factories.py`: 动态 DOCX/PDF/Markdown 夹具工厂。
- `hengwen-api/tests/test_*.py`: 单元、契约、迁移、SSE 和端到端测试。

---

### Task 1: FastAPI 应用骨架、配置和统一错误

**Files:**
- Create: `hengwen-api/.env.example`
- Create: `hengwen-api/.gitignore`
- Modify: `hengwen-api/pyproject.toml`
- Modify: `hengwen-api/src/hengwen_api/__init__.py`
- Create: `hengwen-api/src/hengwen_api/main.py`
- Create: `hengwen-api/src/hengwen_api/core/config.py`
- Create: `hengwen-api/src/hengwen_api/core/exceptions.py`
- Create: `hengwen-api/src/hengwen_api/core/logging.py`
- Create: `hengwen-api/src/hengwen_api/api/v1/router.py`
- Create: `hengwen-api/src/hengwen_api/api/v1/health.py`
- Create: `hengwen-api/src/hengwen_api/schemas/common.py`
- Create: `hengwen-api/tests/test_health.py`

**Interfaces:**
- Produces: `Settings`, `get_settings()`, `AppError`, `CamelModel`, `create_app(settings=None, session_factory=None)`, `app`, `run()`。
- Produces HTTP: `GET /api/v1/health`, `/api/docs`, `/api/redoc`, `/api/openapi.json`。

`.env.example` 使用精确变量名 `HENGWEN_ENV`、`HENGWEN_HOST`、`HENGWEN_PORT`、`HENGWEN_DATABASE_URL`、`HENGWEN_STORAGE_DIR`、`HENGWEN_MAX_FILE_SIZE_MB` 和 `HENGWEN_CORS_ORIGINS`。异常枚举必须包含 `INVALID_FILE_TYPE`、`FILE_TOO_LARGE`、`INVALID_DOCUMENT`、`DOCUMENT_NOT_FOUND`、`TASK_NOT_FOUND`、`REPORT_NOT_FOUND`、`INVALID_TASK_STATE`、`REVIEW_FAILED` 和 `DATABASE_ERROR`。

- [ ] **Step 1: 写配置、健康检查和错误契约的失败测试**

```python
from fastapi.testclient import TestClient

from hengwen_api.core.config import Settings
from hengwen_api.main import create_app


def test_health_contract() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "hengwen-api",
        "version": "0.1.0",
    }
    assert response.headers["x-request-id"].startswith("req_")


def test_openapi_is_mounted_below_api() -> None:
    client = TestClient(create_app(Settings()))
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/redoc").status_code == 200
    assert client.get("/api/openapi.json").status_code == 200


def test_cors_origins_are_parsed_from_csv() -> None:
    settings = Settings(cors_origins="http://localhost:5173,http://127.0.0.1:5173")
    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
```

- [ ] **Step 2: 运行测试并确认因应用模块缺失而失败**

Run: `cd hengwen-api && uv run pytest tests/test_health.py -q`

Expected: collection fails with `ModuleNotFoundError` for `hengwen_api.main` or `hengwen_api.core.config`。

- [ ] **Step 3: 实现最小应用工厂和公共 Schema**

```python
def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
```

`Settings` 使用 `env_prefix="HENGWEN_"`，提供 host、port、database_url、storage_dir、max_file_size_mb、cors_origins、SSE 间隔和日志级别。`create_app()` 配置 docs URL、request ID middleware、异常 handlers、CORS 和 v1 router。`run()` 使用 uvicorn 启动 `hengwen_api.main:app`。

- [ ] **Step 4: 修复 CLI 入口并加固忽略规则**

```toml
[project.scripts]
hengwen-api = "hengwen_api.main:run"
```

`hengwen-api/.gitignore` 必须包含：

```gitignore
.env
storage/
*.db
*.sqlite
*.sqlite3
```

- [ ] **Step 5: 运行任务测试和静态检查**

Run: `cd hengwen-api && uv run pytest tests/test_health.py -q`

Expected: `3 passed`。

Run: `cd hengwen-api && uv run ruff check src tests/test_health.py`

Expected: exit 0。

- [ ] **Step 6: 提交应用骨架**

```bash
git add hengwen-api/.env.example hengwen-api/.gitignore hengwen-api/pyproject.toml hengwen-api/src hengwen-api/tests/test_health.py
git diff --staged --check
git commit -m "feat(api): bootstrap FastAPI application"
```

提交前运行 SQLite 跟踪检查，匹配结果必须为空：

```powershell
git ls-files | Select-String -Pattern '(?i)(\.db$|\.sqlite$|\.sqlite3$)'
```

---

### Task 2: SQLAlchemy 核心模型、Session 和 Alembic

**Files:**
- Create: `hengwen-api/alembic.ini`
- Create: `hengwen-api/alembic/env.py`
- Create: `hengwen-api/alembic/script.py.mako`
- Create: `hengwen-api/alembic/versions/20260813_0001_init_core_tables.py`
- Create: `hengwen-api/src/hengwen_api/db/base.py`
- Create: `hengwen-api/src/hengwen_api/db/session.py`
- Create: `hengwen-api/src/hengwen_api/models/__init__.py`
- Create: `hengwen-api/src/hengwen_api/models/document.py`
- Create: `hengwen-api/src/hengwen_api/models/review_task.py`
- Create: `hengwen-api/src/hengwen_api/models/review_issue.py`
- Create: `hengwen-api/src/hengwen_api/models/task_event.py`
- Create: `hengwen-api/src/hengwen_api/repositories/document_repository.py`
- Create: `hengwen-api/src/hengwen_api/repositories/review_repository.py`
- Create: `hengwen-api/tests/test_migrations.py`
- Create: `hengwen-api/tests/test_repositories.py`

**Interfaces:**
- Produces: `Base`, `SessionFactory = sessionmaker[Session]`, `create_engine_for_url(url)`, `create_session_factory(engine) -> SessionFactory`, `DocumentRepository`, `ReviewRepository`。
- Produces models: `Document`, `ReviewTask`, `ReviewIssue`, `TaskEvent`。

- [ ] **Step 1: 写临时 SQLite 迁移和 Repository 失败测试**

```python
def test_alembic_upgrade_creates_core_tables(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'migration.sqlite').as_posix()}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    inspector = inspect(create_engine(database_url))
    assert {"documents", "review_tasks", "review_issues", "task_events"} <= set(
        inspector.get_table_names()
    )


def test_document_repository_round_trip(db_session: Session) -> None:
    document = DocumentRepository(db_session).create(
        original_name="论文.docx",
        stored_name="generated.docx",
        file_type=".docx",
        file_size=128,
        file_hash="a" * 64,
        storage_path="uploads/2026/08/generated.docx",
    )
    db_session.commit()
    assert DocumentRepository(db_session).get(document.id).original_name == "论文.docx"
```

- [ ] **Step 2: 运行测试并确认核心表和类型缺失**

Run: `cd hengwen-api && uv run pytest tests/test_migrations.py tests/test_repositories.py -q`

Expected: collection or migration fails because models/repositories/revision do not exist。

- [ ] **Step 3: 实现 typed models 和 SessionFactory**

所有主键使用 `BigInteger().with_variant(Integer, "sqlite")` 保证 SQLite 自增；外部 ID 使用长度固定字符串；时间字段使用 `DateTime(timezone=True)`；JSON 事件数据使用 `JSON`。关系必须明确外键和 cascade，不依赖隐式表名推断。

```python
class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
```

- [ ] **Step 4: 实现首个 Alembic revision**

Revision 创建四表、外键、唯一约束和以下索引：document created/status、task task_id/report_id/document_id/status/created_at、issue task_id/created_at、event task_id/id/created_at。Downgrade 按反序移除索引和表。

- [ ] **Step 5: 实现 Repository 最小 CRUD 和分页查询**

`DocumentRepository` 提供 create/get；`ReviewRepository` 提供 create_task/get_task/get_task_by_report/add_issues/add_event/list_events/list_completed_reports/count_completed_reports。所有查询返回 ORM 实体列表或实体，不返回 Row tuple。

- [ ] **Step 6: 运行迁移与 Repository 测试**

Run: `cd hengwen-api && uv run pytest tests/test_migrations.py tests/test_repositories.py -q`

Expected: all pass；数据库文件只出现在 pytest 临时目录。

- [ ] **Step 7: 提交持久化层**

```bash
git add hengwen-api/alembic.ini hengwen-api/alembic hengwen-api/src/hengwen_api/db hengwen-api/src/hengwen_api/models hengwen-api/src/hengwen_api/repositories hengwen-api/tests/test_migrations.py hengwen-api/tests/test_repositories.py
git diff --staged --check
git commit -m "feat(db): add core persistence models"
```

---

### Task 3: 安全文档上传

**Files:**
- Create: `hengwen-api/src/hengwen_api/schemas/document.py`
- Create: `hengwen-api/src/hengwen_api/services/document_service.py`
- Create: `hengwen-api/src/hengwen_api/api/dependencies.py`
- Create: `hengwen-api/src/hengwen_api/api/v1/documents.py`
- Modify: `hengwen-api/src/hengwen_api/api/v1/router.py`
- Create: `hengwen-api/tests/conftest.py`
- Create: `hengwen-api/tests/factories.py`
- Create: `hengwen-api/tests/test_upload.py`

**Interfaces:**
- Produces: `DocumentResponse`, `DocumentService.store(upload: UploadFile) -> Document`, `POST /api/v1/documents`。
- Consumes: `Settings`, `DocumentRepository`, request-scoped SQLAlchemy Session。

- [ ] **Step 1: 写上传成功和安全失败测试**

```python
def test_upload_docx_uses_generated_path(client: TestClient, docx_bytes: bytes) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("../../论文.docx", docx_bytes, DOCX_MIME)},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "论文.docx"
    assert body["fileType"] == ".docx"
    assert body["fileHash"] == hashlib.sha256(docx_bytes).hexdigest()
    assert ".." not in body.get("storagePath", "")


@pytest.mark.parametrize("name", ["paper.exe", "paper.doc", "paper.docx.exe"])
def test_rejects_invalid_extension(client: TestClient, name: str) -> None:
    response = client.post("/api/v1/documents", files={"file": (name, b"x")})
    assert response.status_code == 415
    assert response.json()["code"] == "INVALID_FILE_TYPE"


def test_rejects_fake_pdf_and_removes_partial_file(client: TestClient, storage_dir: Path) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("fake.pdf", b"not-pdf", "application/pdf")},
    )
    assert response.status_code == 422
    assert list(storage_dir.rglob("*.*")) == []
```

同一测试文件加入以下边界测试：

```python
def test_rejects_file_larger_than_configured_limit(small_limit_client: TestClient) -> None:
    response = small_limit_client.post(
        "/api/v1/documents",
        files={"file": ("large.md", b"a" * 1025, "text/markdown")},
    )
    assert response.status_code == 413
    assert response.json()["code"] == "FILE_TOO_LARGE"


def test_rejects_corrupt_docx(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("broken.docx", b"PK-not-openxml", DOCX_MIME)},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_DOCUMENT"


def test_rejects_non_utf8_markdown(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("broken.md", b"\xff\xfe\x00", "text/markdown")},
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("filename", "content", "mime"),
    [
        ("valid.pdf", build_pdf_bytes("HengWen PDF"), "application/pdf"),
        ("valid.md", "# 标题\n\n正文".encode(), "text/markdown"),
    ],
)
def test_accepts_valid_pdf_and_markdown(client, filename, content, mime) -> None:
    response = client.post(
        "/api/v1/documents", files={"file": (filename, content, mime)}
    )
    assert response.status_code == 201
    assert response.json()["fileHash"] == hashlib.sha256(content).hexdigest()
```

- [ ] **Step 2: 运行上传测试并确认 endpoint 缺失**

Run: `cd hengwen-api && uv run pytest tests/test_upload.py -q`

Expected: requests return 404 because documents router is not registered。

- [ ] **Step 3: 实现流式大小限制、真实类型验证和原子保存**

以固定 chunk 读取 UploadFile 到目标年月目录下的 `.part` 临时文件，累计字节数超过限制立即抛出 `FILE_TOO_LARGE`。校验函数必须验证 DOCX ZIP/OpenXML 主文档、PDF header、UTF-8/UTF-8-SIG Markdown。校验通过后用 `Path.replace()` 原子改名；数据库失败时删除最终文件。

- [ ] **Step 4: 实现文档 Schema 和 endpoint**

返回 201 和 camelCase 字段：`id`、`filename`、`fileType`、`fileSize`、`fileHash`、`status`、`createdAt`。不返回绝对路径。

- [ ] **Step 5: 运行上传测试和回归测试**

Run: `cd hengwen-api && uv run pytest tests/test_upload.py tests/test_health.py -q`

Expected: all pass。

- [ ] **Step 6: 提交上传链路**

```bash
git add hengwen-api/src/hengwen_api/api hengwen-api/src/hengwen_api/schemas/document.py hengwen-api/src/hengwen_api/services/document_service.py hengwen-api/tests
git diff --staged --check
git commit -m "feat(document): implement secure document upload"
```

---

### Task 4: 统一文档模型和三种解析器

**Files:**
- Modify: `hengwen-api/pyproject.toml`
- Modify: `hengwen-api/uv.lock`
- Create: `hengwen-api/src/hengwen_api/document_engine/models.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/parser.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/docx_parser.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/markdown_parser.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/pdf_parser.py`
- Create: `hengwen-api/tests/test_docx_parser.py`
- Create: `hengwen-api/tests/test_markdown_parser.py`
- Create: `hengwen-api/tests/test_pdf_parser.py`

**Interfaces:**
- Produces: `DocumentModel`, `ParagraphModel`, `RunModel`, `HeadingModel`, `TableModel`, `FigureModel`, `ReferenceModel`。
- Produces: `parse_document(path: Path, file_type: str) -> DocumentModel`。

- [ ] **Step 1: 通过 uv 添加唯一新增依赖**

Run: `cd hengwen-api && uv add pypdf`

Expected: `pyproject.toml` 和 `uv.lock` 只新增 pypdf 解析依赖及必要锁定信息；不使用 pip。

- [ ] **Step 2: 写 DOCX 中间模型失败测试**

```python
def test_docx_parser_extracts_runs_headings_tables_and_sections(tmp_path: Path) -> None:
    path = build_structured_docx(tmp_path / "structured.docx")
    model = parse_document(path, ".docx")
    assert model.raw_text.startswith("衡文测试论文")
    assert model.headings[0].text == "1 绪论"
    assert model.headings[0].level == 1
    assert model.paragraphs[1].runs[0].font_name == "宋体"
    assert model.paragraphs[1].runs[0].font_size == 12.0
    assert len(model.tables) == 1
    assert len(model.sections) == 1
```

Markdown 测试断言标题层级、引用和参考文献；PDF 测试使用 `PdfWriter` 生成页面并断言文本提取。另测试空文档和未知类型抛 `INVALID_DOCUMENT` 或 `INVALID_FILE_TYPE`。

- [ ] **Step 3: 运行解析器测试并确认模块缺失**

Run: `cd hengwen-api && uv run pytest tests/test_docx_parser.py tests/test_markdown_parser.py tests/test_pdf_parser.py -q`

Expected: collection fails because document engine modules do not exist。

- [ ] **Step 4: 实现统一 dataclass 模型和 parser dispatcher**

中间模型使用类型明确的 dataclass，不依赖 python-docx 类。Parser dispatcher 仅按受支持 file_type 调用对应 parser；解析器不访问 HTTP 或数据库。

- [ ] **Step 5: 实现 DOCX、Markdown 和 PDF 解析器**

DOCX 解析显式 Run 属性并回退到段落样式，补读 eastAsia 字体；Heading level 从内置样式或 outline level 获取。Markdown 支持 ATX/Setext 标题和参考文献段。PDF 使用 `PdfReader`，加密或无可提取文本时抛出安全 `INVALID_DOCUMENT`。

- [ ] **Step 6: 运行解析测试和格式检查**

Run: `cd hengwen-api && uv run pytest tests/test_docx_parser.py tests/test_markdown_parser.py tests/test_pdf_parser.py -q`

Expected: all pass。

Run: `cd hengwen-api && uv run ruff check src/hengwen_api/document_engine tests/test_*parser.py`

Expected: exit 0。

- [ ] **Step 7: 提交解析器**

```bash
git add hengwen-api/pyproject.toml hengwen-api/uv.lock hengwen-api/src/hengwen_api/document_engine hengwen-api/tests/test_docx_parser.py hengwen-api/tests/test_markdown_parser.py hengwen-api/tests/test_pdf_parser.py hengwen-api/tests/factories.py
git diff --staged --check
git commit -m "feat(parser): add unified document parsers"
```

---

### Task 5: 独立规则、Issue 和确定性评分

**Files:**
- Create: `hengwen-api/src/hengwen_api/document_engine/rules/base.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/rules/format_rules.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/rules/structure_rules.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/rules/caption_rules.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/rules/reference_rules.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/rule_engine.py`
- Create: `hengwen-api/src/hengwen_api/document_engine/scoring.py`
- Create: `hengwen-api/tests/test_rule_engine.py`
- Create: `hengwen-api/tests/test_scoring.py`

**Interfaces:**
- Produces: `Rule` Protocol、`RuleIssue`、`RuleEngine.review(document, check_format, check_citation) -> list[RuleIssue]`。
- Produces: `score_issues(issues) -> ScoreResult(score: int, verdict: Verdict)`。

- [ ] **Step 1: 写评分边界失败测试**

```python
@pytest.mark.parametrize(
    ("severities", "score", "verdict"),
    [
        ([], 100, "pass"),
        (["warning", "info"], 96, "pass"),
        (["error"], 92, "pending"),
        (["error"] * 3, 76, "fail"),
        (["error"] * 13, 0, "fail"),
    ],
)
def test_scoring_is_deterministic(severities, score, verdict) -> None:
    issues = [make_issue(severity=value) for value in severities]
    assert score_issues(issues) == ScoreResult(score=score, verdict=verdict)
    assert score_issues(issues) == score_issues(issues)
```

- [ ] **Step 2: 写规则编号、开关和格式适用范围失败测试**

对 `FMT001-FMT006`、`STR001-STR005`、`CAP001-CAP004`、`REF001-REF003` 分别提供最小 DocumentModel，断言触发时 rule_code、severity、location、original、suggestion 完整；修复输入后断言不触发。额外断言 PDF/Markdown 不运行 Word 专属 FMT 规则，`check_citation=false` 不运行 REF 规则。

- [ ] **Step 3: 运行规则测试并确认缺少实现**

Run: `cd hengwen-api && uv run pytest tests/test_scoring.py tests/test_rule_engine.py -q`

Expected: collection fails because rule_engine/scoring modules do not exist。

- [ ] **Step 4: 实现规则 Protocol、分类规则和稳定排序**

每条规则为独立 class，固定 `code` 和 `category`，只接收 `DocumentModel`。RuleEngine 按 `(category order, rule code, location, original)` 稳定排序。无法可靠判断时返回空列表，不生成猜测 Issue。

- [ ] **Step 5: 实现评分器**

```python
PENALTIES = {"error": 8, "warning": 3, "info": 1}
SERIOUS_ERROR_THRESHOLD = 3


def score_issues(issues: Sequence[RuleIssue]) -> ScoreResult:
    score = max(0, 100 - sum(PENALTIES[item.severity] for item in issues))
    error_count = sum(item.severity == "error" for item in issues)
    if score < 70 or error_count >= SERIOUS_ERROR_THRESHOLD:
        verdict = "fail"
    elif error_count == 0 and score >= 90:
        verdict = "pass"
    else:
        verdict = "pending"
    return ScoreResult(score=score, verdict=verdict)
```

- [ ] **Step 6: 运行规则与解析器回归**

Run: `cd hengwen-api && uv run pytest tests/test_rule_engine.py tests/test_scoring.py tests/test_docx_parser.py -q`

Expected: all pass，重复运行产生相同 Issue 内容、排序、score 和 verdict。

- [ ] **Step 7: 提交规则系统**

```bash
git add hengwen-api/src/hengwen_api/document_engine hengwen-api/tests/test_rule_engine.py hengwen-api/tests/test_scoring.py
git diff --staged --check
git commit -m "feat(review): add deterministic rule engine"
```

---

### Task 6: 持久任务事件、ReviewWorker 和服务编排

**Files:**
- Create: `hengwen-api/src/hengwen_api/ai/reviewer.py`
- Create: `hengwen-api/src/hengwen_api/events/models.py`
- Create: `hengwen-api/src/hengwen_api/events/repository.py`
- Create: `hengwen-api/src/hengwen_api/events/emitter.py`
- Create: `hengwen-api/src/hengwen_api/schemas/review.py`
- Create: `hengwen-api/src/hengwen_api/services/review_service.py`
- Create: `hengwen-api/src/hengwen_api/workers/review_worker.py`
- Create: `hengwen-api/tests/test_review_task.py`

**Interfaces:**
- Produces: `AIReviewer.review(document: DocumentModel) -> list[RuleIssue]` 和 `NullAIReviewer.review(document: DocumentModel) -> list[RuleIssue]`。
- Produces: `TaskEventEmitter.emit(session: Session, task: ReviewTask, event_type: str, message: str, level: str = "info", data: dict[str, object] | None = None) -> TaskEvent`。
- Produces: `ReviewService.create_task(document_id: int, settings: ReviewSettingsCreate) -> ReviewTask` 和 `ReviewWorker.run(task_id: str) -> None`。
- Consumes: parser、RuleEngine、score_issues、Repositories、SessionFactory。

- [ ] **Step 1: 写任务状态机和不支持能力失败测试**

```python
def test_worker_completes_task_and_persists_ordered_events(
    session_factory: SessionFactory, stored_docx: Document
) -> None:
    task = create_review_task(session_factory, stored_docx, check_format=True)
    ReviewWorker(session_factory).run(task.task_id)
    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert saved.status == "completed"
    assert saved.progress == 100
    assert saved.stage == "completed"
    assert saved.report_id.startswith("report_")
    assert [event.event_type for event in events][0] == "task.started"
    assert [event.event_type for event in events][-1] == "task.completed"


def test_plagiarism_request_records_unsupported_event_without_fake_result(
    session_factory: SessionFactory,
    stored_docx: Document,
) -> None:
    task = create_review_task(
        session_factory,
        stored_docx,
        check_plagiarism=True,
    )
    ReviewWorker(session_factory).run(task.task_id)
    with session_factory() as session:
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert any(event.message == "unsupported capability: plagiarism" for event in events)
    assert all("重复率" not in json.dumps(event.data_json, ensure_ascii=False) for event in events)
```

同一测试文件加入明确的失败和恢复测试：

```python
def test_parser_failure_persists_safe_failed_state(
    session_factory: SessionFactory,
    stored_corrupt_docx: Document,
) -> None:
    task = create_review_task(session_factory, stored_corrupt_docx)
    ReviewWorker(session_factory).run(task.task_id)
    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert saved.status == "failed"
    assert saved.error_message == "无法解析该文档"
    assert events[-1].event_type == "task.failed"
    assert "Traceback" not in events[-1].message


def test_startup_recovery_fails_stale_tasks(session_factory: SessionFactory) -> None:
    task = create_pending_task(session_factory)
    recover_stale_tasks(session_factory)
    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert saved.status == "failed"
    assert events[-1].event_type == "task.failed"
    assert events[-1].data_json["reason"] == "application_restarted"
```

- [ ] **Step 2: 运行任务测试并确认 Worker 缺失**

Run: `cd hengwen-api && uv run pytest tests/test_review_task.py -q`

Expected: collection fails because services/workers/events modules do not exist。

- [ ] **Step 3: 实现 EventEmitter 和 NullAIReviewer**

Emitter 在调用方现有 Session 中添加 `TaskEvent`，不自行 commit，确保任务状态与事件处于同一事务。NullAIReviewer 返回空 Issue 集合和明确 skipped 状态，不生成文本。

- [ ] **Step 4: 实现 ReviewService**

Service 校验 document 存在且可审查，生成 `rvw_<uuid>`，保存 settings 和 created 状态。`autoReport` 原样持久化；MVP 的结构化 Report 是每个任务的必需结果，因此该开关不抑制结果实体，它只保留给后续自动导出/跳转行为。

- [ ] **Step 5: 实现 ReviewWorker 阶段事务**

按 read、format、citation、suggestion、completed 执行。每阶段提交状态和事件；Issue 行与 `issue.detected` 事件同事务写入。完成时计算 word_count、score、verdict、report_id 和 completed_at。失败时先回滚，再使用新 Session 保存 failed 状态和安全事件。

- [ ] **Step 6: 实现启动恢复**

`recover_stale_tasks(session_factory)` 将启动时遗留的 pending/running 任务标为 failed，保存 `REVIEW_FAILED` 安全摘要和 `task.failed` 恢复事件，不自动重跑。

- [ ] **Step 7: 运行任务、规则和 Repository 回归**

Run: `cd hengwen-api && uv run pytest tests/test_review_task.py tests/test_rule_engine.py tests/test_repositories.py -q`

Expected: all pass。

- [ ] **Step 8: 提交任务系统**

```bash
git add hengwen-api/src/hengwen_api/ai hengwen-api/src/hengwen_api/events hengwen-api/src/hengwen_api/schemas/review.py hengwen-api/src/hengwen_api/services/review_service.py hengwen-api/src/hengwen_api/workers hengwen-api/tests/test_review_task.py
git diff --staged --check
git commit -m "feat(task): add persistent review task events"
```

---

### Task 7: Review API、SSE 和 Report API

**Files:**
- Create: `hengwen-api/src/hengwen_api/schemas/report.py`
- Create: `hengwen-api/src/hengwen_api/api/v1/review_tasks.py`
- Create: `hengwen-api/src/hengwen_api/api/v1/reports.py`
- Modify: `hengwen-api/src/hengwen_api/api/v1/router.py`
- Modify: `hengwen-api/src/hengwen_api/main.py`
- Create: `hengwen-api/tests/test_report_api.py`
- Create: `hengwen-api/tests/test_sse.py`
- Create: `hengwen-api/tests/test_end_to_end.py`

**Interfaces:**
- Produces HTTP: create/query task、SSE、report list/detail。
- Produces Schema: `AnalysisTaskResponse`、`TaskStatusResponse`、`TaskEventResponse`、`IssueResponse`、`ReportResponse`、`ReportPageResponse`。

- [ ] **Step 1: 写 create/query task 和 report 契约失败测试**

```python
def test_create_task_matches_analysis_task_contract(client, uploaded_document_id) -> None:
    response = client.post(
        "/api/v1/review-tasks",
        json={
            "documentId": uploaded_document_id,
            "settings": {
                "orgName": "",
                "standard": "本科毕业论文规范（默认）",
                "checkFormat": True,
                "checkCitation": True,
                "checkPlagiarism": False,
                "autoReport": True,
            },
        },
    )
    assert response.status_code == 202
    assert set(response.json()) == {
        "id", "filename", "fileType", "stageIndex", "progress", "startedAt"
    }
    assert response.json()["id"].startswith("rvw_")


def test_report_detail_matches_react_contract(client, completed_task) -> None:
    response = client.get(f"/api/v1/reports/{completed_task.report_id}")
    assert response.status_code == 200
    assert set(response.json()) == {
        "id", "filename", "fileType", "checkedAt", "wordCount",
        "score", "verdict", "issues",
    }
```

分页测试断言 page/pageSize/total/items；不存在资源断言标准错误 code 和 requestId。

在 `test_end_to_end.py` 同时先写完整链路测试，使其在路由实现前因 404 失败：

```python
def test_docx_review_end_to_end(client: TestClient, valid_thesis_docx: bytes) -> None:
    upload = client.post(
        "/api/v1/documents",
        files={"file": ("毕业论文.docx", valid_thesis_docx, DOCX_MIME)},
    )
    assert upload.status_code == 201
    task = client.post(
        "/api/v1/review-tasks",
        json={"documentId": upload.json()["id"], "settings": REVIEW_SETTINGS},
    )
    assert task.status_code == 202
    status = client.get(f"/api/v1/review-tasks/{task.json()['id']}")
    assert status.json()["status"] == "completed"
    report_id = status.json()["reportId"]
    report = client.get(f"/api/v1/reports/{report_id}")
    assert report.status_code == 200
    assert report.json()["filename"] == "毕业论文.docx"
    assert report.json()["wordCount"] > 0
    assert report.json()["issues"]
    history = client.get("/api/v1/reports?page=1&pageSize=20")
    assert any(item["id"] == report_id for item in history.json()["items"])
```

- [ ] **Step 2: 写 SSE 顺序和断线恢复失败测试**

```python
def test_sse_replays_events_after_last_event_id(client, completed_task) -> None:
    all_events = read_sse(client, completed_task.task_id)
    cursor = all_events[1]["id"]
    resumed = read_sse(client, completed_task.task_id, headers={"Last-Event-ID": str(cursor)})
    assert all(event["id"] > cursor for event in resumed)
    assert resumed[-1]["event"] == "task.completed"
    assert resumed[-1]["data"]["progress"] == 100
```

同一测试文件加入 keepalive、最终关闭和 camelCase 断言：

```python
def test_sse_emits_keepalive_while_task_is_running(running_task_client, running_task) -> None:
    chunks = read_sse_chunks(running_task_client, running_task.task_id, limit=1)
    assert chunks == [": keepalive"]


@pytest.mark.parametrize("final_event", ["task.completed", "task.failed"])
def test_sse_closes_after_final_event(client, persisted_final_task, final_event) -> None:
    events = read_sse(client, persisted_final_task(final_event).task_id)
    assert events[-1]["event"] == final_event
    assert set(events[-1]["data"]) >= {
        "eventId", "taskId", "eventType", "stageIndex", "progress"
    }
```

测试 Settings 将 keepalive 和 poll interval 固定为 `0.01` 秒，使测试不依赖真实 15 秒等待。

- [ ] **Step 3: 运行 API 测试并确认路由缺失**

Run: `cd hengwen-api && uv run pytest tests/test_report_api.py tests/test_sse.py tests/test_end_to_end.py -q`

Expected: review-tasks/reports endpoints return 404。

- [ ] **Step 4: 实现 task endpoints 和 BackgroundTasks 提交**

创建 endpoint 在数据库提交任务后调用 `background_tasks.add_task(ReviewWorker(session_factory).run, task_id)`，返回 202。查询 endpoint 返回 stage/status/progress，并保持 AnalysisTask 字段。

- [ ] **Step 5: 实现 SSE 持久轮询**

同步 generator 每轮使用新 Session 查询 `id > cursor`，按 ID 发送；空闲达到 keepalive 间隔输出 `: keepalive\n\n`；读取到 task.completed/task.failed 后发送并 return。Header 使用 `Last-Event-ID` alias，非法负数返回验证错误。

- [ ] **Step 6: 实现 Report 详情和分页组装**

从 completed ReviewTask 联合 Document 和 ReviewIssue 组装响应；issues 按规则和创建顺序稳定排序。列表只返回 completed 且 report_id 非空的任务，page 从 1 开始，pageSize 限制 1..100。

- [ ] **Step 7: 运行 API、SSE 和任务回归**

Run: `cd hengwen-api && uv run pytest tests/test_report_api.py tests/test_sse.py tests/test_end_to_end.py tests/test_review_task.py -q`

Expected: all pass，SSE 测试不挂起。

- [ ] **Step 8: 提交 API 和 SSE**

```bash
git add hengwen-api/src/hengwen_api/api hengwen-api/src/hengwen_api/schemas hengwen-api/src/hengwen_api/main.py hengwen-api/tests/test_report_api.py hengwen-api/tests/test_sse.py hengwen-api/tests/test_end_to_end.py
git diff --staged --check
git commit -m "feat(api): expose review progress and reports"
```

---

### Task 8: 错误边界、日志安全和操作文档

**Files:**
- Modify: `hengwen-api/README.md`
- Modify: `hengwen-api/src/hengwen_api/core/exceptions.py`
- Modify: `hengwen-api/src/hengwen_api/core/logging.py`
- Modify: `hengwen-api/src/hengwen_api/services/document_service.py`
- Modify: `hengwen-api/src/hengwen_api/workers/review_worker.py`
- Create: `hengwen-api/tests/test_errors.py`

**Interfaces:**
- Verifies exception sanitization、request ID propagation、文件补偿清理和安全日志字段。

- [ ] **Step 1: 写数据库异常和日志泄露失败测试**

```python
def test_database_exception_returns_safe_envelope(database_failure_client) -> None:
    response = database_failure_client.post(
        "/api/v1/documents",
        files={"file": ("paper.md", b"# title", "text/markdown")},
    )
    assert response.status_code == 500
    assert response.json()["code"] == "DATABASE_ERROR"
    assert response.json()["requestId"].startswith("req_")
    assert "sqlite" not in json.dumps(response.json()).lower()


def test_database_failure_removes_saved_file(database_failure_client, storage_dir) -> None:
    database_failure_client.post(
        "/api/v1/documents",
        files={"file": ("paper.md", b"# title", "text/markdown")},
    )
    assert list(storage_dir.rglob("*.*")) == []


def test_logs_do_not_include_document_body_or_database_password(client, caplog) -> None:
    secret_body = "正文秘密内容"
    client.post(
        "/api/v1/documents",
        files={"file": ("paper.md", secret_body.encode(), "text/markdown")},
    )
    rendered = "\n".join(record.getMessage() for record in caplog.records)
    assert secret_body not in rendered
    assert "password" not in rendered.lower()
```

- [ ] **Step 2: 运行错误测试并确认补偿清理或异常映射失败**

Run: `cd hengwen-api && uv run pytest tests/test_errors.py -q -x`

Expected: 至少一个断言因缺少数据库异常映射、文件补偿删除或日志过滤而失败。

- [ ] **Step 3: 实现最小异常映射、补偿删除和日志过滤**

数据库异常转换为 `DATABASE_ERROR`，document service 在 flush/commit 失败时删除最终文件，日志只记录 ID、阶段、duration 和异常类名。先重跑 `test_errors.py -q -x`，再重跑上传和任务测试。

- [ ] **Step 4: 补全 README 操作说明**

README 必须写明 uv sync、Alembic upgrade、两种启动方式、环境变量、API 列表、SQLite 禁止提交、DOCX/Markdown/PDF 能力边界、查重/AI 限制和质量命令。

- [ ] **Step 5: 运行完整 pytest**

Run: `cd hengwen-api && uv run pytest -q`

Expected: all tests pass，无 warning 被静默忽略。

- [ ] **Step 6: 提交端到端和文档**

```bash
git add hengwen-api/README.md hengwen-api/src/hengwen_api/core/exceptions.py hengwen-api/src/hengwen_api/core/logging.py hengwen-api/src/hengwen_api/services/document_service.py hengwen-api/src/hengwen_api/workers/review_worker.py hengwen-api/tests/test_errors.py
git diff --staged --check
git commit -m "test(review): cover backend MVP end to end"
```

---

### Task 9: 完整质量门禁和真实运行验证

**Files:**
- Modify only files required by a failing verified gate

**Interfaces:**
- Verifies install、lint、format、types、tests、migration、CLI、health、Swagger 和真实 API 链路。

- [ ] **Step 1: 同步依赖并运行静态门禁**

Run:

```bash
cd hengwen-api
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Expected: every command exits 0。失败时按具体诊断最小修复，然后从失败命令开始重跑并补跑全部静态门禁。

- [ ] **Step 2: 运行完整测试和迁移**

Run:

```bash
cd hengwen-api
uv run pytest -q
uv run alembic upgrade head
```

迁移验证必须将 `HENGWEN_DATABASE_URL` 指向临时目录或已忽略的 `storage/`。Expected: all tests pass and migration reaches head。

- [ ] **Step 3: 启动真实 CLI 并验证 HTTP**

Run: `cd hengwen-api && uv run hengwen-api`

在独立请求中验证：

```text
GET http://127.0.0.1:8000/api/v1/health -> 200 and exact health JSON
GET http://127.0.0.1:8000/api/docs -> 200
GET http://127.0.0.1:8000/api/openapi.json -> 200
```

再使用动态生成 DOCX 调用上传、创建任务、SSE 或任务查询、报告详情和报告列表。保存命令摘要，不提交生成文件。

- [ ] **Step 4: 审计 Git 范围和 SQLite 防线**

Run:

```powershell
git status --short
git diff --check
git ls-files | Select-String -Pattern '(?i)(\.db$|\.sqlite$|\.sqlite3$)'
git diff -- hengwen-web
```

Expected: SQLite 查询无输出；`git diff -- hengwen-web` 无输出；没有 storage、日志、用户文档、`.env` 或构建产物。

- [ ] **Step 5: 修复门禁后创建最终聚焦提交**

仅当门禁修复产生改动时暂存确切文件并提交：

```bash
git add -- hengwen-api/.env.example hengwen-api/.gitignore hengwen-api/README.md hengwen-api/alembic.ini hengwen-api/alembic hengwen-api/pyproject.toml hengwen-api/uv.lock hengwen-api/src hengwen-api/tests
git diff --staged --check
git commit -m "fix(api): satisfy backend quality gates"
```

若没有门禁修复，不创建空提交。

- [ ] **Step 6: 生成交付报告**

报告列出实际修改文件、层间关系、全部 API、四表和 revision、三类解析边界、Worker/Event/SSE 链路、每个验证命令的真实结果、已知限制和必要下一步。不得把构建、静态阅读或单元测试单独表述为 React 已接入或腾讯云 MySQL 已联调。
