import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from backend.agent.desk_status import desk_status
from backend.agent.factory import build_agent
from backend.agent.itsm_tryon import try_itsm
from backend.agent.langfuse_trace import flush_callback, make_callback, traced_invoke
from backend.agent.mock_http import MockHttp
from backend.agent.run_context import RunContext, clear_run_context, set_run_context
from backend.agent.run_hub import RunChannel, RunHub
from backend.agent.stream_mapper import map_agent_stream
from backend.agent.user_message import build_user_message
from backend.models.appeal import Appeal
from backend.models.appeal_event import AppealEvent
from backend.models.appeal_message import AppealMessage
from backend.repositories.appeal_repository import AppealRepository
from backend.settings import Settings

logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(
        self,
        settings: Settings,
        hub: RunHub,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._settings = settings
        self._hub = hub
        self._sf = session_factory
        self._agent = None

    async def start(self, appeal_id: int, reply_text: str | None = None) -> None:
        channel = self._hub.open(appeal_id)
        asyncio.create_task(self._run(appeal_id, channel, reply_text))

    async def _run(self, appeal_id: int, channel: RunChannel, reply_text: str | None) -> None:
        mock = MockHttp(self._settings.mock_severholod_url, timeout=5.0)
        try:
            await channel.emit({"type": "run_started", "appeal_id": appeal_id})
            async with self._sf() as session:
                repo = AppealRepository(session)
                appeal = await repo.get(appeal_id)
                if appeal is None:
                    await channel.emit({"type": "run_error", "detail": "Обращение не найдено"})
                    return
                ctx = RunContext(
                    appeal_id=appeal_id,
                    card=appeal.card,
                    mock=mock,
                    received_at=appeal.received_at,
                )
                set_run_context(ctx)
                result: dict[str, Any] = {
                    "messages": [],
                    "persist": [],
                }
                try:
                    result = await asyncio.wait_for(
                        self._invoke(appeal, reply_text, channel, ctx),
                        timeout=self._settings.agent_timeout_seconds,
                    )
                except TimeoutError:
                    logger.exception("agent timeout")
                except Exception:
                    logger.exception("agent invoke failed")
                await self._emit_trace(channel, repo, appeal, result, ctx)
                outcome = apply_card_decision(ctx.card, mock)
                await _commit_finish(channel, repo, appeal, ctx, outcome)
        except Exception:
            logger.exception("agent run failed")
            await self._fail(appeal_id, channel, "Прогон упал")
        finally:
            clear_run_context()
            mock.close()
            channel.close()

    async def _invoke(
        self,
        appeal: Appeal,
        reply_text: str | None,
        channel: RunChannel,
        ctx: RunContext,
    ) -> dict[str, Any]:
        if self._agent is None:
            self._agent = build_agent(self._settings)
        handler = make_callback(self._settings, appeal.id)
        try:

            async def on_event(payload: dict[str, Any]) -> None:
                await channel.emit(payload)
                if (
                    payload.get("type") == "tool_result"
                    and payload.get("name") == "update_card"
                    and ctx.snapshots
                ):
                    await channel.emit({"type": "card_updated", "card": ctx.snapshots[-1]})

            async def run_stream() -> dict[str, Any]:
                stream = await self._agent.astream_events(
                    {
                        "messages": [
                            {"role": "user", "content": build_user_message(appeal, reply_text)}
                        ]
                    },
                    version="v3",
                    config={
                        "callbacks": [handler] if handler is not None else [],
                        "metadata": {
                            "langfuse_session_id": str(appeal.id),
                            "langfuse_trace_name": "reflex-appeal",
                            "appeal_id": str(appeal.id),
                        },
                        "configurable": {"thread_id": str(appeal.id)},
                        "recursion_limit": 40,
                    },
                )
                return await map_agent_stream(stream, on_event)

            return await traced_invoke(appeal.id, run_stream)
        finally:
            flush_callback(handler)

    async def _emit_trace(
        self,
        channel: RunChannel,
        repo: AppealRepository,
        appeal: Appeal,
        result: dict[str, Any],
        _ctx: RunContext,
    ) -> None:
        for event in result.get("persist") or []:
            if isinstance(event, dict):
                await _persist_event(channel, repo, appeal.id, event)

    async def _fail(self, appeal_id: int, channel: RunChannel, detail: str) -> None:
        try:
            async with self._sf() as session:
                repo = AppealRepository(session)
                appeal = await repo.get(appeal_id)
                if appeal is not None:
                    appeal.run_status = "idle"
                    appeal.status = "dispatch"
                    await repo.add_event(
                        AppealEvent(
                            appeal_id=appeal.id,
                            type="run_finished",
                            card_snapshot=appeal.card,
                        )
                    )
                    await repo.commit()
        except Exception:
            logger.exception("fail persist")
        await channel.emit({"type": "run_error", "detail": detail})
        await channel.emit(
            {
                "type": "run_finished",
                "run_status": "idle",
                "outcome": "dispatch",
                "status": "dispatch",
                "auto_in_prod": False,
            }
        )


def apply_card_decision(card: dict[str, Any], mock: MockHttp) -> str:
    decision = card.setdefault("decision", {})
    if not isinstance(decision, dict):
        card["decision"] = {}
        decision = card["decision"]
    outcome = str(decision.get("outcome") or "dispatch")
    if outcome in {"create", "update"}:
        try_itsm(mock, card, outcome)
        return outcome
    decision["ticket_draft"] = None
    decision["itsm_dry_run"] = None
    decision["auto_in_prod"] = False
    return outcome


async def _commit_finish(
    channel: RunChannel,
    repo: AppealRepository,
    appeal: Appeal,
    ctx: RunContext,
    outcome: str,
) -> None:
    appeal.card = ctx.card
    flag_modified(appeal, "card")
    appeal.status = desk_status(outcome)
    appeal.run_status = "idle"
    await repo.add_event(
        AppealEvent(appeal_id=appeal.id, type="run_finished", card_snapshot=ctx.card)
    )
    await repo.commit()
    await channel.emit({"type": "card_updated", "card": ctx.card})
    await channel.emit(
        {
            "type": "run_finished",
            "run_status": "idle",
            "outcome": outcome,
            "status": appeal.status,
            "auto_in_prod": bool((ctx.card.get("decision") or {}).get("auto_in_prod")),
        }
    )


async def _persist_event(
    channel: RunChannel,
    repo: AppealRepository,
    appeal_id: int,
    event: dict[str, Any],
) -> None:
    kind = str(event.get("type") or "")
    if kind == "thought":
        text = event.get("text")
        if isinstance(text, str) and text.strip():
            await _note(channel, repo, appeal_id, "thought", {"text": text}, emit=False)
        return
    if kind == "tool_call":
        await _note(
            channel,
            repo,
            appeal_id,
            "tool_call",
            {"id": event.get("id"), "name": event.get("name"), "args": event.get("args")},
            emit=False,
        )
        return
    if kind == "tool_result":
        body = {key: value for key, value in event.items() if key != "type"}
        await _note(channel, repo, appeal_id, "tool_result", body, emit=False)
        return
    if kind == "message_final":
        text = event.get("text")
        if isinstance(text, str) and text:
            await _note(
                channel,
                repo,
                appeal_id,
                "message",
                {"text": text},
                event="message_final",
                emit=False,
            )


async def _note(
    channel: RunChannel,
    repo: AppealRepository,
    appeal_id: int,
    kind: str,
    body: dict[str, Any],
    event: str | None = None,
    *,
    emit: bool = True,
) -> None:
    await repo.add_message(AppealMessage(appeal_id=appeal_id, author="agent", kind=kind, body=body))
    if emit:
        await channel.emit({"type": event or kind, **body} if event else {"type": kind, **body})
