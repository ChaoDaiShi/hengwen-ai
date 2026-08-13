import logging

from fastapi.testclient import TestClient

from hengwen_api.core.config import Settings
from hengwen_api.core.logging import LOG_FORMAT, RequestContextFormatter
from hengwen_api.main import create_app


def test_health_contract() -> None:
    client = TestClient(create_app(Settings()))

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "hengwen-api",
        "version": "0.1.0",
    }
    assert response.headers["x-request-id"].startswith("req_")


def test_openapi_is_mounted_below_api() -> None:
    client = TestClient(create_app(Settings()))

    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/redoc").status_code == 200
    assert client.get("/api/openapi.json").status_code == 200


def test_cors_origins_are_parsed_from_csv() -> None:
    settings = Settings(cors_origins="http://localhost:5173,http://127.0.0.1:5173")

    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_log_formatter_supplies_request_id_for_third_party_records() -> None:
    record = logging.LogRecord(
        name="httpx",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )

    rendered = RequestContextFormatter(LOG_FORMAT).format(record)

    assert "request_id=-" in rendered
