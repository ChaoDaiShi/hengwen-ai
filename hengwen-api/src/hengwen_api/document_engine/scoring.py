from collections.abc import Sequence
from dataclasses import dataclass

from hengwen_api.document_engine.models import RuleIssue, Verdict

PENALTIES = {"error": 8, "warning": 3, "info": 1}
SERIOUS_ERROR_THRESHOLD = 3


@dataclass(frozen=True, slots=True)
class ScoreResult:
    score: int
    verdict: Verdict


def score_issues(issues: Sequence[RuleIssue]) -> ScoreResult:
    score = max(0, 100 - sum(PENALTIES[item.severity] for item in issues))
    error_count = sum(item.severity == "error" for item in issues)
    if score < 70 or error_count >= SERIOUS_ERROR_THRESHOLD:
        verdict: Verdict = "fail"
    elif error_count == 0 and score >= 90:
        verdict = "pass"
    else:
        verdict = "pending"
    return ScoreResult(score=score, verdict=verdict)
