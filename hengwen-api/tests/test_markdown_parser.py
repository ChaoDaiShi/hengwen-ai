from pathlib import Path

from hengwen_api.document_engine.parser import parse_document


def test_markdown_parser_extracts_headings_quotes_and_references(
    tmp_path: Path,
) -> None:
    path = tmp_path / "paper.md"
    path.write_text(
        "# 论文标题\n\n> 引用内容\n\n### 研究方法\n\n正文引用[1]。\n\n"
        "## 参考文献\n\n[1] 张三. 文档研究[J]. 测试学报, 2025.\n",
        encoding="utf-8",
    )

    model = parse_document(path, ".md")

    assert [(item.level, item.text) for item in model.headings] == [
        (1, "论文标题"),
        (3, "研究方法"),
        (2, "参考文献"),
    ]
    assert "引用内容" in model.metadata["quotes"]
    assert model.references[0].number == 1
    assert model.word_count > 0


def test_markdown_parser_supports_setext_heading(tmp_path: Path) -> None:
    path = tmp_path / "setext.md"
    path.write_text("标题\n====\n\n正文", encoding="utf-8")

    model = parse_document(path, ".md")

    assert model.headings[0].level == 1
    assert model.headings[0].text == "标题"
