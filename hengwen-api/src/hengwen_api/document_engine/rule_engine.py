from hengwen_api.document_engine.models import DocumentModel, RuleIssue
from hengwen_api.document_engine.rules.base import RuleBase
from hengwen_api.document_engine.rules.caption_rules import CAPTION_RULES
from hengwen_api.document_engine.rules.format_rules import FORMAT_RULES
from hengwen_api.document_engine.rules.reference_rules import REFERENCE_RULES
from hengwen_api.document_engine.rules.structure_rules import STRUCTURE_RULES


class RuleEngine:
    def __init__(self) -> None:
        self.rules: tuple[RuleBase, ...] = (
            *FORMAT_RULES,
            *STRUCTURE_RULES,
            *CAPTION_RULES,
            *REFERENCE_RULES,
        )

    @property
    def rule_codes(self) -> tuple[str, ...]:
        return tuple(rule.code for rule in self.rules)

    def review(
        self,
        document: DocumentModel,
        *,
        check_format: bool,
        check_citation: bool,
    ) -> list[RuleIssue]:
        order = {rule.code: index for index, rule in enumerate(self.rules)}
        issues: list[RuleIssue] = []
        for rule in self.rules:
            if rule.category == "format" and not check_format:
                continue
            if rule.category == "reference" and not check_citation:
                continue
            if rule.docx_only and document.file_type != ".docx":
                continue
            issues.extend(rule.check(document))
        return sorted(
            issues,
            key=lambda item: (
                order[item.rule_code],
                item.location,
                item.original,
            ),
        )
