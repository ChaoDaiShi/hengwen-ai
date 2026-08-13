import pytest

from hengwen_api.document_engine.models import (
    DocumentModel,
    FigureModel,
    HeadingModel,
    ParagraphModel,
    ReferenceModel,
    RuleIssue,
    RunModel,
    TableModel,
)
from hengwen_api.document_engine.rule_engine import RuleEngine


def valid_document() -> DocumentModel:
    paragraphs = [
        ParagraphModel(
            index=0,
            text="衡文测试论文",
            style_name="Title",
            alignment="center",
            runs=[RunModel("衡文测试论文", "黑体", 16.0, True)],
        ),
        ParagraphModel(
            index=1,
            text="摘要",
            style_name="Heading 1",
            runs=[RunModel("摘要", "黑体", 14.0, True)],
        ),
        ParagraphModel(
            index=2,
            text="本文研究文档规范。关键词：文档；规范",
            style_name="Normal",
            alignment="justify",
            line_spacing=1.5,
            runs=[RunModel("本文研究文档规范。关键词：文档；规范", "宋体", 12.0)],
        ),
        ParagraphModel(
            index=3,
            text="1 绪论",
            style_name="Heading 1",
            runs=[RunModel("1 绪论", "黑体", 14.0, True)],
        ),
        ParagraphModel(
            index=4,
            text="这是长度足够的规范正文段落，用于测试规则的正常输入。",
            style_name="Normal",
            alignment="justify",
            line_spacing=1.5,
            runs=[RunModel("这是长度足够的规范正文段落。", "宋体", 12.0)],
        ),
        ParagraphModel(
            index=5,
            text="参考文献",
            style_name="Heading 1",
            runs=[RunModel("参考文献", "黑体", 14.0, True)],
        ),
    ]
    return DocumentModel(
        file_type=".docx",
        paragraphs=paragraphs,
        headings=[
            HeadingModel(0, "衡文测试论文", 0),
            HeadingModel(1, "摘要", 1),
            HeadingModel(3, "1 绪论", 1),
            HeadingModel(5, "参考文献", 1),
        ],
        tables=[TableModel(0, [["字段", "值"]], "表 1 测试表")],
        figures=[FigureModel(0, None, "图 1 测试图")],
        references=[
            ReferenceModel(0, "[1] 张三. 文档研究[J]. 测试学报, 2025, 1(1): 1-8.", 1)
        ],
        raw_text="\n".join(item.text for item in paragraphs),
    )


def document_for(rule_code: str) -> DocumentModel:
    document = valid_document()
    if rule_code == "FMT001":
        document.paragraphs[4].runs.append(RunModel("异体", "仿宋", 12.0))
    elif rule_code == "FMT002":
        document.paragraphs[4].runs.append(RunModel("异号", "宋体", 10.5))
    elif rule_code == "FMT003":
        document.paragraphs.append(
            ParagraphModel(6, "2 研究方法", "Normal", runs=[RunModel("2 研究方法")])
        )
    elif rule_code == "FMT004":
        document.headings.append(HeadingModel(6, "1.1.1 跳级标题", 3))
    elif rule_code == "FMT005":
        document.paragraphs[4].alignment = "right"
    elif rule_code == "FMT006":
        document.paragraphs[4].line_spacing = 4.0
    elif rule_code == "STR001":
        document.headings = [item for item in document.headings if item.level != 0]
        document.paragraphs[0].style_name = "Normal"
    elif rule_code == "STR002":
        document.paragraphs[1].text = "前言"
        document.raw_text = document.raw_text.replace("摘要", "前言")
    elif rule_code == "STR003":
        document.paragraphs[2].text = "本文研究文档规范。"
        document.raw_text = document.raw_text.replace("关键词：文档；规范", "")
    elif rule_code == "STR004":
        document.references = []
        document.paragraphs[5].text = "致谢"
        document.raw_text = document.raw_text.replace("参考文献", "致谢")
    elif rule_code == "STR005":
        document.headings[2] = HeadingModel(3, "3 研究方法", 1)
    elif rule_code == "CAP001":
        document.figures[0].caption = None
    elif rule_code == "CAP002":
        document.tables[0].caption = None
    elif rule_code == "CAP003":
        document.figures.append(FigureModel(1, None, "图 3 结果图"))
    elif rule_code == "CAP004":
        document.tables.append(TableModel(1, [["结果"]], "表 3 结果表"))
    elif rule_code == "REF001":
        document.references.append(
            ReferenceModel(1, "[3] 李四. 研究[J]. 学报, 2025.", 3)
        )
    elif rule_code == "REF002":
        document.references[0] = ReferenceModel(0, "[1] 张三. 未完整文献", 1)
    elif rule_code == "REF003":
        document.raw_text = document.raw_text.replace(
            "这是长度足够", "引用[2]。这是长度足够"
        )
    else:
        raise AssertionError(f"unknown rule code: {rule_code}")
    return document


@pytest.mark.parametrize(
    "rule_code",
    [
        "FMT001",
        "FMT002",
        "FMT003",
        "FMT004",
        "FMT005",
        "FMT006",
        "STR001",
        "STR002",
        "STR003",
        "STR004",
        "STR005",
        "CAP001",
        "CAP002",
        "CAP003",
        "CAP004",
        "REF001",
        "REF002",
        "REF003",
    ],
)
def test_each_registered_rule_emits_complete_issue(rule_code: str) -> None:
    issues = RuleEngine().review(
        document_for(rule_code),
        check_format=True,
        check_citation=True,
    )

    issue = next(item for item in issues if item.rule_code == rule_code)
    assert issue.severity in {"error", "warning", "info"}
    assert issue.title
    assert issue.location
    assert issue.summary
    assert issue.original
    assert issue.suggestion


def test_rule_registry_has_exact_mvp_codes() -> None:
    assert RuleEngine().rule_codes == (
        "FMT001",
        "FMT002",
        "FMT003",
        "FMT004",
        "FMT005",
        "FMT006",
        "STR001",
        "STR002",
        "STR003",
        "STR004",
        "STR005",
        "CAP001",
        "CAP002",
        "CAP003",
        "CAP004",
        "REF001",
        "REF002",
        "REF003",
    )


def test_format_rules_are_disabled_and_not_applied_to_pdf() -> None:
    document = document_for("FMT001")
    disabled = RuleEngine().review(
        document,
        check_format=False,
        check_citation=True,
    )
    document.file_type = ".pdf"
    unsupported = RuleEngine().review(
        document,
        check_format=True,
        check_citation=True,
    )

    assert not any(item.rule_code.startswith("FMT") for item in disabled)
    assert not any(item.rule_code.startswith("FMT") for item in unsupported)


def test_reference_rules_respect_setting() -> None:
    issues = RuleEngine().review(
        document_for("REF003"),
        check_format=True,
        check_citation=False,
    )

    assert not any(item.rule_code.startswith("REF") for item in issues)


def test_rule_results_have_stable_content_and_order() -> None:
    document = document_for("FMT001")
    engine = RuleEngine()

    first = engine.review(document, check_format=True, check_citation=True)
    second = engine.review(document, check_format=True, check_citation=True)

    assert first == second
    assert all(isinstance(item, RuleIssue) for item in first)
    registry_order = {code: index for index, code in enumerate(engine.rule_codes)}
    assert [registry_order[item.rule_code] for item in first] == sorted(
        registry_order[item.rule_code] for item in first
    )
