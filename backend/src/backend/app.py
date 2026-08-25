from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.db import create_engine, create_schema, session_factory
from backend.db_ping import ping_database
from backend.routers.appeals import router as appeals_router
from backend.routers.auth import router as auth_router
from backend.routers.health import router as health_router
from backend.settings import Settings, get_settings


def _error_payload(detail: str) -> dict[str, str]:
    return {"detail": detail}


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = resolved
        engine = create_engine(resolved.database_url)
        app.state.engine = engine
        app.state.session_factory = session_factory(engine)
        if resolved.ping_database:
            await ping_database(resolved.database_url)
        if resolved.ensure_schema:
            await create_schema(engine)
        yield
        await engine.dispose()

    app = FastAPI(title="reflex", lifespan=lifespan)

    @app.exception_handler(HTTPException)
    async def http_exc(_request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(status_code=exc.status_code, content=_error_payload(detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exc(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=_error_payload(str(exc.errors())))

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(appeals_router)
    return app
