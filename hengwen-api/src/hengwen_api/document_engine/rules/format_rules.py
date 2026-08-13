import re
from collections import Counter
from itertools import pairwise

from hengwen_api.document_engine.models import DocumentModel, ParagraphModel
from hengwen_api.document_engine.rules.base import RuleBase

NUMBERED_HEADING = re.compile(r"^\s*\d+(?:\.\d+)*\s+\S+")


def _body_paragraphs(document: DocumentModel) -> list[ParagraphModel]:
    heading_indexes = {item.paragraph_index for item in document.headings}
    return [
        item
        for item in document.paragraphs
        if item.index not in heading_indexes and len(item.text.strip()) >= 8
    ]


class BodyFontConsistencyRule(RuleBase):
    code = "FMT001"
    category = "format"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        runs = [
            run
            for item in _body_paragraphs(document)
            for run in item.runs
            if run.text.strip()
        ]
        names = [run.font_name for run in runs if run.font_name]
        if len(set(names)) <= 1:
            return []
        dominant = Counter(names).most_common(1)[0][0]
        abnormal = next(
            run for run in runs if run.font_name and run.font_name != dominant
        )
        return [
            self.issue(
                title="正文字体不一致",
                location="正文",
                summary=f"正文主要使用{dominant}，检测到{abnormal.font_name}",
                original=abnormal.text,
                suggestion=f"将该处字体统一为{dominant}",
            )
        ]


class BodyFontSizeConsistencyRule(RuleBase):
    code = "FMT002"
    category = "format"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        runs = [
            run
            for item in _body_paragraphs(document)
            for run in item.runs
            if run.text.strip()
        ]
        sizes = [run.font_size for run in runs if run.font_size is not None]
        if len(set(sizes)) <= 1:
            return []
        dominant = Counter(sizes).most_common(1)[0][0]
        abnormal = next(
            run
            for run in runs
            if run.font_size is not None and run.font_size != dominant
        )
        return [
            self.issue(
                title="正文字号不一致",
                location="正文",
                summary=f"正文主要使用 {dominant:g} 磅，检测到 {abnormal.font_size:g} 磅",
                original=abnormal.text,
                suggestion=f"将该处字号统一为 {dominant:g} 磅",
            )
        ]


class HeadingStyleRule(RuleBase):
    code = "FMT003"
    category = "format"
    severity = "error"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        heading_indexes = {item.paragraph_index for item in document.headings}
        candidate = next(
            (
                item
                for item in document.paragraphs
                if NUMBERED_HEADING.match(item.text)
                and item.index not in heading_indexes
            ),
            None,
        )
        if candidate is None:
            return []
        return [
            self.issue(
                title="章节标题未使用标题样式",
                location=f"第 {candidate.index + 1} 段",
                summary="编号文本看起来是标题，但未使用标题样式",
                original=candidate.text,
                suggestion="应用与层级匹配的 Word 标题样式",
            )
        ]


class HeadingLevelJumpRule(RuleBase):
    code = "FMT004"
    category = "format"
    severity = "error"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        levels = [item for item in document.headings if item.level > 0]
        for previous, current in pairwise(levels):
            if current.level > previous.level + 1:
                return [
                    self.issue(
                        title="标题层级跳级",
                        location=current.text,
                        summary=f"标题层级由 {previous.level} 跳到 {current.level}",
                        original=current.text,
                        suggestion=f"改为 {previous.level + 1} 级标题或补充中间层级",
                    )
                ]
        return []


class ParagraphAlignmentRule(RuleBase):
    code = "FMT005"
    category = "format"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        abnormal = next(
            (item for item in _body_paragraphs(document) if item.alignment == "right"),
            None,
        )
        if abnormal is None:
            return []
        return [
            self.issue(
                title="正文段落对齐异常",
                location=f"第 {abnormal.index + 1} 段",
                summary="正文段落使用右对齐",
                original=abnormal.text,
                suggestion="将正文调整为两端对齐或规范要求的对齐方式",
            )
        ]


class LineSpacingRule(RuleBase):
    code = "FMT006"
    category = "format"
    docx_only = True

    def check(self, document: DocumentModel) -> list:
        abnormal = next(
            (
                item
                for item in _body_paragraphs(document)
                if item.line_spacing is not None
                and (item.line_spacing < 0.8 or item.line_spacing > 3.0)
            ),
            None,
        )
        if abnormal is None:
            return []
        return [
            self.issue(
                title="正文行距明显异常",
                location=f"第 {abnormal.index + 1} 段",
                summary=f"检测到行距 {abnormal.line_spacing:g}",
                original=abnormal.text,
                suggestion="按文档规范统一正文行距",
            )
        ]


FORMAT_RULES = (
    BodyFontConsistencyRule(),
    BodyFontSizeConsistencyRule(),
    HeadingStyleRule(),
    HeadingLevelJumpRule(),
    ParagraphAlignmentRule(),
    LineSpacingRule(),
)
