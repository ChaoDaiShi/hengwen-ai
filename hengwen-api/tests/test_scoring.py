import pytest

from hengwen_api.document_engine.models import RuleIssue, Severity
from hengwen_api.document_engine.scoring import ScoreResult, score_issues


def make_issue(severity: Severity) -> RuleIssue:
    return RuleIssue(
        severity=severity,
        title="测试问题",
        location="正文",
        summary="测试摘要",
        original="原文",
        suggestion="建议",
        rule_code="TEST001",
        issue_type="test",
    )


@pytest.mark.parametrize(
    ("severities", "score", "verdict"),
    [
        ([], 100, "pass"),
        (["warning", "info"], 96, "pass"),
        (["error"], 92, "pending"),
        (["error"] * 3, 76, "fail"),
        (["error"] * 13, 0, "fail"),
        (["warning"] * 11, 67, "fail"),
    ],
)
def test_scoring_is_deterministic(
    severities: list[Severity],
    score: int,
    verdict: str,
) -> None:
    issues = [make_issue(value) for value in severities]

    result = score_issues(issues)

    assert result == ScoreResult(score=score, verdict=verdict)
    assert score_issues(issues) == result
