import re

from hengwen_api.document_engine.models import DocumentModel
from hengwen_api.document_engine.rules.base import RuleBase

CITATION = re.compile(r"\[(\d+)\]")


class ReferenceNumberContinuityRule(RuleBase):
    code = "REF001"
    category = "reference"

    def check(self, document: DocumentModel) -> list:
        numbers = [
            item.number for item in document.references if item.number is not None
        ]
        if numbers == list(range(1, len(numbers) + 1)):
            return []
        return [
            self.issue(
                title="参考文献编号不连续",
                location="参考文献",
                summary=f"检测到参考文献编号序列 {numbers}",
                original="；".join(item.text for item in document.references),
                suggestion="从 1 开始连续编排参考文献编号",
            )
        ]


class GbtFieldPresenceRule(RuleBase):
    code = "REF002"
    category = "reference"

    def check(self, document: DocumentModel) -> list:
        incomplete = next(
            (
                item
                for item in document.references
                if not re.search(r"\[(?:J|M|D|C|N|R|S|P|EB/OL)\]", item.text)
                or not re.search(r"(?:19|20)\d{2}", item.text)
            ),
            None,
        )
        if incomplete is None:
            return []
        return [
            self.issue(
                title="参考文献常见字段缺失",
                location=f"参考文献第 {incomplete.index + 1} 条",
                summary="条目缺少文献类型标识或出版年份",
                original=incomplete.text,
                suggestion="按 GB/T 7714 补全文献类型、年份等字段",
            )
        ]


class CitationRangeRule(RuleBase):
    code = "REF003"
    category = "reference"
    severity = "error"

    def check(self, document: DocumentModel) -> list:
        reference_numbers = {
            item.number for item in document.references if item.number is not None
        }
        cited_numbers = {int(value) for value in CITATION.findall(document.raw_text)}
        invalid = sorted(cited_numbers - reference_numbers)
        if not invalid:
            return []
        number = invalid[0]
        return [
            self.issue(
                title="正文引用超出参考文献范围",
                location="正文引用",
                summary=f"正文引用 [{number}] 没有对应参考文献",
                original=f"[{number}]",
                suggestion="补充对应参考文献或修正正文引用编号",
            )
        ]


REFERENCE_RULES = (
    ReferenceNumberContinuityRule(),
    GbtFieldPresenceRule(),
    CitationRangeRule(),
)
