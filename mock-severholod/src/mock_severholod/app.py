from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mock_severholod.exception_handlers import register_exception_handlers
from mock_severholod.routers.contracts import router as contracts_router
from mock_severholod.routers.crm import router as crm_router
from mock_severholod.routers.eam import router as eam_router
from mock_severholod.routers.health import router as health_router
from mock_severholod.routers.itsm import router as itsm_router
from mock_severholod.seed_store import SeedStore
from mock_severholod.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = resolved
        app.state.store = SeedStore(resolved.seed_path)
        yield

    app = FastAPI(title="mock-severholod", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(crm_router)
    app.include_router(eam_router)
    app.include_router(contracts_router)
    app.include_router(itsm_router)
    return app


app = create_app()
