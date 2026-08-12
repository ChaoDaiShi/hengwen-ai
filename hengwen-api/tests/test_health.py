from fastapi.testclient import TestClient

from hengwen_api.core.config import Settings
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
