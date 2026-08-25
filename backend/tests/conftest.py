import asyncio

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.app import create_app
from backend.settings import Settings


def test_settings() -> Settings:
    return Settings(
        openai_api_key=SecretStr("test-openai"),
        openai_base_url="https://openrouter.ai/api/v1",
        openai_model="qwen/qwen3.6-35b-a3b",
        langfuse_public_key="pk-lf-test",
        langfuse_secret_key=SecretStr("sk-lf-test"),
        langfuse_host="http://langfuse:3000",
        database_url="postgresql+asyncpg://reflex:reflex@localhost:5432/reflex",
        session_secret=SecretStr("session-secret-for-tests"),
        dispatcher_login="dispatcher",
        dispatcher_password=SecretStr("secret"),
        mock_severholod_url="http://mock-severholod:8080",
        ping_database=False,
        ensure_schema=False,
    )


def _wipe(database_url: str) -> None:
    async def go() -> None:
        engine = create_async_engine(database_url)
        try:
            async with engine.begin() as conn:
                await conn.execute(text("TRUNCATE appeals RESTART IDENTITY CASCADE"))
        finally:
            await engine.dispose()

    asyncio.run(go())


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app(test_settings())) as test_client:
        yield test_client


@pytest.fixture
def db_client() -> TestClient:
    settings = test_settings().model_copy(update={"ping_database": True, "ensure_schema": True})
    app = create_app(settings)
    with TestClient(app) as test_client:
        _wipe(settings.database_url)
        yield test_client
        _wipe(settings.database_url)
