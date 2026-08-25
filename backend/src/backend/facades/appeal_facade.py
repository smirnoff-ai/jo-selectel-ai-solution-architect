from datetime import date, datetime
from typing import Any

from backend.agent.dispatcher_report import attach_report_if_missing
from backend.card_template import empty_card
from backend.models.appeal import Appeal
from backend.models.appeal_event import AppealEvent
from backend.models.appeal_message import AppealMessage
from backend.repositories.appeal_repository import DESK_STATUSES, AppealRepository, new_appeal

PREVIEW = 80


class AppealNotFoundError(Exception):
    pass


def text_preview(text: str) -> str:
    if len(text) <= PREVIEW:
        return text
    return f"{text[:PREVIEW]}…"


def _row(appeal: Appeal) -> dict[str, Any]:
    return {
        "id": appeal.id,
        "received_at": appeal.received_at.isoformat(),
        "channel": appeal.channel,
        "sender": appeal.sender,
        "text_preview": text_preview(appeal.text),
        "run_status": appeal.run_status,
        "status": appeal.status,
        "created_by": appeal.created_by,
    }


class AppealFacade:
    def __init__(self, repo: AppealRepository) -> None:
        self._repo = repo

    async def create(
        self,
        *,
        channel: str,
        sender: str | None,
        received_at: datetime,
        text: str,
        attachment_text: str | None,
        created_by: str,
    ) -> dict[str, Any]:
        card = empty_card(
            channel=channel,
            sender=sender,
            received_at=received_at,
            text=text,
            attachment_text=attachment_text,
        )
        appeal = new_appeal(
            channel=channel,
            sender=sender,
            received_at=received_at,
            text=text,
            attachment_text=attachment_text,
            created_by=created_by,
            card=card,
        )
        await self._repo.add(appeal)
        await self._repo.add_event(
            AppealEvent(appeal_id=appeal.id, type="created", card_snapshot=card),
        )
        appeal.run_status = "running"
        await self._repo.commit()
        return {"id": appeal.id, "status": appeal.status, "run_status": appeal.run_status}

    async def desk(self) -> dict[str, Any]:
        widgets = []
        for status in DESK_STATUSES:
            recent = await self._repo.recent_by_status(status)
            widgets.append(
                {
                    "status": status,
                    "count": await self._repo.count_by_status(status),
                    "recent": [
                        {
                            "id": row.id,
                            "received_at": row.received_at.isoformat(),
                            "channel": row.channel,
                            "sender": row.sender,
                            "text_preview": text_preview(row.text),
                            "run_status": row.run_status,
                        }
                        for row in recent
                    ],
                }
            )
        return {"widgets": widgets}

    async def journal(
        self,
        *,
        status: str | None,
        channel: str | None,
        received_from: date | None,
        received_to: date | None,
    ) -> dict[str, Any]:
        rows = await self._repo.list_journal(
            status=status,
            channel=channel,
            received_from=received_from,
            received_to=received_to,
        )
        return {"items": [_row(item) for item in rows]}

    async def get(self, appeal_id: int) -> dict[str, Any]:
        appeal = await self._repo.get(appeal_id)
        if appeal is None:
            raise AppealNotFoundError
        auto = appeal.card.get("decision", {}).get("auto_in_prod")
        return {
            "id": appeal.id,
            "status": appeal.status,
            "run_status": appeal.run_status,
            "created_by": appeal.created_by,
            "auto_in_prod": bool(auto) if auto is not None else False,
            "card": appeal.card,
        }

    async def messages(self, appeal_id: int) -> dict[str, Any]:
        appeal = await self._repo.get(appeal_id)
        if appeal is None:
            raise AppealNotFoundError
        rows = await self._repo.list_messages(appeal_id)
        items = [
            {
                "id": row.id,
                "author": row.author,
                "kind": row.kind,
                "body": row.body,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
        tool_names = [
            str(row.body.get("name"))
            for row in rows
            if row.kind == "tool_result" and isinstance(row.body, dict) and row.body.get("name")
        ]
        created_at = rows[-1].created_at.isoformat() if rows else appeal.received_at.isoformat()
        message_id = (rows[-1].id + 1) if rows else 1
        return {
            "items": attach_report_if_missing(
                appeal.card,
                items,
                tool_names=tool_names,
                message_id=message_id,
                created_at=created_at,
            )
        }

    async def reply(self, appeal_id: int, text: str, created_by: str) -> dict[str, Any]:
        appeal = await self._repo.get(appeal_id)
        if appeal is None:
            raise AppealNotFoundError
        await self._repo.add_message(
            AppealMessage(
                appeal_id=appeal.id,
                author=created_by,
                kind="dispatcher_reply",
                body={"text": text},
            )
        )
        await self._repo.add_event(
            AppealEvent(appeal_id=appeal.id, type="dispatcher_reply", card_snapshot=None),
        )
        appeal.run_status = "running"
        await self._repo.commit()
        return {"id": appeal.id, "run_status": appeal.run_status}
