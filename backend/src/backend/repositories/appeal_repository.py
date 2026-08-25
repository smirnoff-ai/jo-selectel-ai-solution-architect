from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.appeal import Appeal
from backend.models.appeal_event import AppealEvent
from backend.models.appeal_message import AppealMessage

DESK_STATUSES = ("new", "clarify", "dispatch", "approve")
RECENT_LIMIT = 5


class AppealRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, appeal: Appeal) -> Appeal:
        self._session.add(appeal)
        await self._session.flush()
        return appeal

    async def add_message(self, message: AppealMessage) -> AppealMessage:
        self._session.add(message)
        await self._session.flush()
        return message

    async def add_event(self, event: AppealEvent) -> AppealEvent:
        self._session.add(event)
        await self._session.flush()
        return event

    async def get(self, appeal_id: int) -> Appeal | None:
        return await self._session.get(Appeal, appeal_id)

    async def list_messages(self, appeal_id: int) -> list[AppealMessage]:
        stmt = (
            select(AppealMessage)
            .where(AppealMessage.appeal_id == appeal_id)
            .order_by(AppealMessage.created_at.asc())
        )
        return list((await self._session.scalars(stmt)).all())

    async def count_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(Appeal).where(Appeal.status == status)
        return int(await self._session.scalar(stmt) or 0)

    async def recent_by_status(self, status: str) -> list[Appeal]:
        stmt = (
            select(Appeal)
            .where(Appeal.status == status)
            .order_by(Appeal.received_at.desc())
            .limit(RECENT_LIMIT)
        )
        return list((await self._session.scalars(stmt)).all())

    async def list_journal(
        self,
        *,
        status: str | None,
        channel: str | None,
        received_from: date | None,
        received_to: date | None,
    ) -> list[Appeal]:
        stmt: Select[tuple[Appeal]] = select(Appeal)
        if status:
            stmt = stmt.where(Appeal.status == status)
        if channel:
            stmt = stmt.where(Appeal.channel == channel)
        if received_from:
            stmt = stmt.where(func.date(Appeal.received_at) >= received_from)
        if received_to:
            stmt = stmt.where(func.date(Appeal.received_at) <= received_to)
        stmt = stmt.order_by(Appeal.received_at.desc())
        return list((await self._session.scalars(stmt)).all())

    async def commit(self) -> None:
        await self._session.commit()

    async def delete_all(self) -> None:
        await self._session.execute(delete(AppealEvent))
        await self._session.execute(delete(AppealMessage))
        await self._session.execute(delete(Appeal))
        await self._session.commit()


def new_appeal(
    *,
    channel: str,
    sender: str | None,
    received_at: datetime,
    text: str,
    attachment_text: str | None,
    created_by: str,
    card: dict[str, Any],
) -> Appeal:
    return Appeal(
        status="new",
        run_status="idle",
        channel=channel,
        sender=sender,
        received_at=received_at,
        text=text,
        attachment_text=attachment_text,
        created_by=created_by,
        card=card,
    )
