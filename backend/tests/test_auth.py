import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.settings import Settings


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_ok(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"login": "dispatcher", "password": "secret"})
    assert response.status_code == 200
    assert response.json() == {"login": "dispatcher"}
    assert "reflex_session" in response.cookies


def test_login_bad_password(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"login": "dispatcher", "password": "nope"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_me_requires_cookie(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_after_login(client: TestClient) -> None:
    client.post("/api/v1/auth/login", json={"login": "dispatcher", "password": "secret"})
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json() == {"login": "dispatcher"}


def test_logout(client: TestClient) -> None:
    client.post("/api/v1/auth/login", json={"login": "dispatcher", "password": "secret"})
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_settings_fail_fast_without_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_HOST",
        "DATABASE_URL",
        "SESSION_SECRET",
        "DISPATCHER_LOGIN",
        "DISPATCHER_PASSWORD",
        "MOCK_SEVERHOLOD_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
