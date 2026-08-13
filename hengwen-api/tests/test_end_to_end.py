from fastapi.testclient import TestClient

from tests.factories import DOCX_MIME
from tests.test_report_api import REVIEW_SETTINGS


def test_docx_review_end_to_end(
    client: TestClient,
    valid_thesis_docx: bytes,
) -> None:
    upload = client.post(
        "/api/v1/documents",
        files={"file": ("毕业论文.docx", valid_thesis_docx, DOCX_MIME)},
    )
    assert upload.status_code == 201

    task = client.post(
        "/api/v1/review-tasks",
        json={"documentId": upload.json()["id"], "settings": REVIEW_SETTINGS},
    )
    assert task.status_code == 202

    status = client.get(f"/api/v1/review-tasks/{task.json()['id']}")
    assert status.json()["status"] == "completed"
    report_id = status.json()["reportId"]

    events = client.get(f"/api/v1/review-tasks/{task.json()['id']}/events")
    assert "event: task.completed" in events.text
    assert "event: issue.detected" in events.text

    report = client.get(f"/api/v1/reports/{report_id}")
    assert report.status_code == 200
    assert report.json()["filename"] == "毕业论文.docx"
    assert report.json()["wordCount"] > 0
    assert report.json()["issues"]

    history = client.get("/api/v1/reports?page=1&pageSize=20")
    assert any(item["id"] == report_id for item in history.json()["items"])
