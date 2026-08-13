from typing import Protocol

from hengwen_api.document_engine.models import DocumentModel, RuleIssue


class AIReviewer(Protocol):
    def review(self, document: DocumentModel) -> list[RuleIssue]: ...


class NullAIReviewer:
    def review(self, document: DocumentModel) -> list[RuleIssue]:
        del document
        return []
