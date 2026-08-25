from collections.abc import AsyncIterator
from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.deps import require_login
from backend.facades.appeal_facade import AppealFacade, AppealNotFoundError
from backend.repositories.appeal_repository import AppealRepository

router = APIRouter(prefix="/api/v1/appeals")

Channel = Literal["email", "telegram", "call", "lk"]


class AppealCreate(BaseModel):
    channel: Channel
    received_at: datetime
    text: str = Field(min_length=1)
    sender: str | None = None
    attachment_text: str | None = None


class ReplyBody(BaseModel):
    text: str = Field(min_length=1)


def _facade(session: AsyncSession) -> AppealFacade:
    return AppealFacade(AppealRepository(session))


@router.get("/desk")
async def desk(
    _login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, object]:
    return await _facade(session).desk()


@router.get("")
async def journal(
    _login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
    status: Annotated[str | None, Query()] = None,
    channel: Annotated[str | None, Query()] = None,
    received_from: Annotated[date | None, Query()] = None,
    received_to: Annotated[date | None, Query()] = None,
) -> dict[str, object]:
    status_f = None if status in (None, "all") else status
    channel_f = None if channel in (None, "all") else channel
    return await _facade(session).journal(
        status=status_f,
        channel=channel_f,
        received_from=received_from,
        received_to=received_to,
    )


@router.post("", status_code=201)
async def create_appeal(
    body: AppealCreate,
    login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, object]:
    return await _facade(session).create(
        channel=body.channel,
        sender=body.sender,
        received_at=body.received_at,
        text=body.text,
        attachment_text=body.attachment_text,
        created_by=login,
    )


@router.get("/{appeal_id}")
async def get_appeal(
    appeal_id: int,
    _login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, object]:
    try:
        return await _facade(session).get(appeal_id)
    except AppealNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Обращение не найдено") from exc


@router.get("/{appeal_id}/messages")
async def list_messages(
    appeal_id: int,
    _login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, object]:
    try:
        return await _facade(session).messages(appeal_id)
    except AppealNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Обращение не найдено") from exc


@router.post("/{appeal_id}/replies", status_code=202)
async def reply(
    appeal_id: int,
    body: ReplyBody,
    login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, object]:
    try:
        return await _facade(session).reply(appeal_id, body.text, login)
    except AppealNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Обращение не найдено") from exc


@router.get("/{appeal_id}/stream")
async def stream(
    appeal_id: int,
    _login: Annotated[str, Depends(require_login)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StreamingResponse:
    try:
        await _facade(session).get(appeal_id)
    except AppealNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Обращение не найдено") from exc

    async def frames() -> AsyncIterator[str]:
        payload = '{"run_status":"idle","note":"agent not started"}'
        yield f"event: run_finished\ndata: {payload}\n\n"

    return StreamingResponse(
        frames(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
