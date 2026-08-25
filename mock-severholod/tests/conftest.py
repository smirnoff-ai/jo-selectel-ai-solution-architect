import pytest
from fastapi.testclient import TestClient

from mock_severholod.app import create_app
from mock_severholod.settings import Settings


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings())
    with TestClient(app) as test_client:
        yield test_client
