from fastapi import Request

from mock_severholod.seed_store import SeedStore
from mock_severholod.settings import Settings


def get_store(request: Request) -> SeedStore:
    return request.app.state.store


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings
