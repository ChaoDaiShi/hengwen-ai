from typing import ClassVar, Literal, Protocol

from hengwen_api.document_engine.models import DocumentModel, RuleIssue, Severity

RuleCategory = Literal["format", "structure", "caption", "reference"]


class Rule(Protocol):
    code: ClassVar[str]
    category: ClassVar[RuleCategory]
    severity: ClassVar[Severity]
    docx_only: ClassVar[bool]

    def check(self, document: DocumentModel) -> list[RuleIssue]: ...


class RuleBase:
    code: ClassVar[str]
    category: ClassVar[RuleCategory]
    severity: ClassVar[Severity] = "warning"
    docx_only: ClassVar[bool] = False

    def check(self, document: DocumentModel) -> list[RuleIssue]:
        raise NotImplementedError

    def issue(
        self,
        *,
        title: str,
        location: str,
        summary: str,
        original: str,
        suggestion: str,
    ) -> RuleIssue:
        return RuleIssue(
            severity=self.severity,
            title=title,
            location=location,
            summary=summary,
            original=original,
            suggestion=suggestion,
            rule_code=self.code,
            issue_type=self.category,
        )
