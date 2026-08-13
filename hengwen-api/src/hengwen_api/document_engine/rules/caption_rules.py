import re

from hengwen_api.document_engine.models import DocumentModel
from hengwen_api.document_engine.rules.base import RuleBase

CAPTION_NUMBER = re.compile(r"^[图表]\s*(\d+)(?:[-.]\d+)?")


def _numbers(captions: list[str]) -> list[int]:
    return [
        int(match.group(1))
        for caption in captions
        if (match := CAPTION_NUMBER.match(caption.strip()))
    ]


class FigureCaptionPresenceRule(RuleBase):
    code = "CAP001"
    category = "caption"

    def check(self, document: DocumentModel) -> list:
        figure = next((item for item in document.figures if not item.caption), None)
        if figure is None:
            return []
        return [
            self.issue(
                title="图题缺失",
                location=f"第 {figure.index + 1} 幅图",
                summary="图片附近未识别到图题",
                original=f"图像关系 {figure.relationship_id or '未知'}",
                suggestion="在图片下方增加连续编号的图题",
            )
        ]


class TableCaptionPresenceRule(RuleBase):
    code = "CAP002"
    category = "caption"

    def check(self, document: DocumentModel) -> list:
        table = next((item for item in document.tables if not item.caption), None)
        if table is None:
            return []
        return [
            self.issue(
                title="表题缺失",
                location=f"第 {table.index + 1} 个表格",
                summary="表格附近未识别到表题",
                original=" | ".join(table.rows[0]) if table.rows else "空表格",
                suggestion="在表格上方增加连续编号的表题",
            )
        ]


class FigureNumberContinuityRule(RuleBase):
    code = "CAP003"
    category = "caption"

    def check(self, document: DocumentModel) -> list:
        captions = [item.caption for item in document.figures if item.caption]
        numbers = _numbers(captions)
        if numbers == list(range(1, len(numbers) + 1)):
            return []
        return [
            self.issue(
                title="图编号不连续",
                location="图题",
                summary=f"检测到图编号序列 {numbers}",
                original="；".join(captions),
                suggestion="按出现顺序连续编排图编号",
            )
        ]


class TableNumberContinuityRule(RuleBase):
    code = "CAP004"
    category = "caption"

    def check(self, document: DocumentModel) -> list:
        captions = [item.caption for item in document.tables if item.caption]
        numbers = _numbers(captions)
        if numbers == list(range(1, len(numbers) + 1)):
            return []
        return [
            self.issue(
                title="表编号不连续",
                location="表题",
                summary=f"检测到表编号序列 {numbers}",
                original="；".join(captions),
                suggestion="按出现顺序连续编排表编号",
            )
        ]


CAPTION_RULES = (
    FigureCaptionPresenceRule(),
    TableCaptionPresenceRule(),
    FigureNumberContinuityRule(),
    TableNumberContinuityRule(),
)
