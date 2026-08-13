import re

from hengwen_api.document_engine.models import DocumentModel
from hengwen_api.document_engine.rules.base import RuleBase

TOP_LEVEL_NUMBER = re.compile(r"^\s*(\d+)\s+")


class TitlePresenceRule(RuleBase):
    code = "STR001"
    category = "structure"
    severity = "error"

    def check(self, document: DocumentModel) -> list:
        if any(item.level == 0 and item.text.strip() for item in document.headings):
            return []
        return [
            self.issue(
                title="缺少文档标题",
                location="文档开头",
                summary="未识别到明确的主标题",
                original=document.paragraphs[0].text
                if document.paragraphs
                else "文档开头为空",
                suggestion="在文档开头增加明确的主标题",
            )
        ]


class AbstractPresenceRule(RuleBase):
    code = "STR002"
    category = "structure"
    severity = "error"

    def check(self, document: DocumentModel) -> list:
        if re.search(r"(^|\n)\s*摘要\s*($|\n)", document.raw_text):
            return []
        return [
            self.issue(
                title="缺少摘要",
                location="标题之后",
                summary="文档中未发现摘要章节",
                original=document.raw_text[:80] or "文档无正文",
                suggestion="在正文前增加摘要章节",
            )
        ]


class KeywordsAfterAbstractRule(RuleBase):
    code = "STR003"
    category = "structure"

    def check(self, document: DocumentModel) -> list:
        if "摘要" not in document.raw_text or re.search(
            r"关\s*键\s*词\s*[:：]", document.raw_text
        ):
            return []
        return [
            self.issue(
                title="摘要后缺少关键词",
                location="摘要",
                summary="摘要章节后未识别到关键词",
                original="摘要内容",
                suggestion="在摘要后增加三至五个关键词",
            )
        ]


class ReferencesSectionRule(RuleBase):
    code = "STR004"
    category = "structure"
    severity = "error"

    def check(self, document: DocumentModel) -> list:
        if document.references or "参考文献" in document.raw_text:
            return []
        return [
            self.issue(
                title="缺少参考文献章节",
                location="文档末尾",
                summary="未识别到参考文献章节",
                original=document.raw_text[-80:] or "文档无正文",
                suggestion="在文档末尾增加参考文献章节",
            )
        ]


class HeadingNumberContinuityRule(RuleBase):
    code = "STR005"
    category = "structure"

    def check(self, document: DocumentModel) -> list:
        numbered = [
            (item, int(match.group(1)))
            for item in document.headings
            if item.level == 1 and (match := TOP_LEVEL_NUMBER.match(item.text))
        ]
        numbers = [number for _item, number in numbered]
        if not numbers or numbers == list(range(1, len(numbers) + 1)):
            return []
        item, _number = numbered[0]
        return [
            self.issue(
                title="标题编号明显断裂",
                location=item.text,
                summary=f"检测到一级标题编号序列 {numbers}",
                original=item.text,
                suggestion="从 1 开始连续编排一级标题编号",
            )
        ]


STRUCTURE_RULES = (
    TitlePresenceRule(),
    AbstractPresenceRule(),
    KeywordsAfterAbstractRule(),
    ReferencesSectionRule(),
    HeadingNumberContinuityRule(),
)
