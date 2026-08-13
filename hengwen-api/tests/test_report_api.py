from fastapi.testclient import TestClient

REVIEW_SETTINGS = {
    "orgName": "",
    "standard": "本科毕业论文规范（默认）",
    "checkFormat": True,
    "checkCitation": True,
    "checkPlagiarism": False,
    "autoReport": True,
}


def create_completed_task(client: TestClient, document_id: int) -> tuple[str, str]:
    response = client.post(
        "/api/v1/review-tasks",
        json={"documentId": document_id, "settings": REVIEW_SETTINGS},
    )
    assert response.status_code == 202
    task_id = str(response.json()["id"])
    status = client.get(f"/api/v1/review-tasks/{task_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"
    return task_id, str(status.json()["reportId"])


def test_create_task_matches_analysis_task_contract(
    client: TestClient,
    uploaded_document_id: int,
) -> None:
    response = client.post(
        "/api/v1/review-tasks",
        json={"documentId": uploaded_document_id, "settings": REVIEW_SETTINGS},
    )

    assert response.status_code == 202
    assert set(response.json()) == {
        "id",
        "filename",
        "fileType",
        "stageIndex",
        "progress",
        "startedAt",
    }
    assert response.json()["id"].startswith("rvw_")
    assert response.json()["filename"] == "毕业论文.docx"
    assert response.json()["fileType"] == ".docx"


def test_task_query_exposes_recovery_state(
    client: TestClient,
    uploaded_document_id: int,
) -> None:
    task_id, report_id = create_completed_task(client, uploaded_document_id)

    response = client.get(f"/api/v1/review-tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["stage"] == "completed"
    assert response.json()["stageIndex"] == 4
    assert response.json()["progress"] == 100
    assert response.json()["status"] == "completed"
    assert response.json()["reportId"] == report_id


def test_report_detail_matches_react_contract(
    client: TestClient,
    uploaded_document_id: int,
) -> None:
    _task_id, report_id = create_completed_task(client, uploaded_document_id)

    response = client.get(f"/api/v1/reports/{report_id}")

    assert response.status_code == 200
    assert set(response.json()) == {
        "id",
        "filename",
        "fileType",
        "checkedAt",
        "wordCount",
        "score",
        "verdict",
        "issues",
    }
    assert response.json()["id"] == report_id
    assert response.json()["filename"] == "毕业论文.docx"
    assert response.json()["wordCount"] > 0
    assert response.json()["issues"]
    assert set(response.json()["issues"][0]) == {
        "id",
        "severity",
        "title",
        "location",
        "summary",
        "original",
        "suggestion",
    }


def test_report_list_is_paginated(
    client: TestClient,
    uploaded_document_id: int,
) -> None:
    _task_id, report_id = create_completed_task(client, uploaded_document_id)

    response = client.get("/api/v1/reports?page=1&pageSize=1")

    assert response.status_code == 200
    assert response.json()["page"] == 1
    assert response.json()["pageSize"] == 1
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [report_id]


def test_missing_task_and_report_use_safe_error_contract(client: TestClient) -> None:
    missing_task = client.get("/api/v1/review-tasks/rvw_missing")
    missing_report = client.get("/api/v1/reports/report_missing")

    assert missing_task.status_code == 404
    assert missing_task.json()["code"] == "TASK_NOT_FOUND"
    assert missing_report.status_code == 404
    assert missing_report.json()["code"] == "REPORT_NOT_FOUND"
    assert missing_report.json()["requestId"].startswith("req_")
