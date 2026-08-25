import asyncio
import json
import logging
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from backend.agent.dispatcher_report import (
    build_dispatcher_report,
    persist_has_message_final,
    tool_names_from_persist,
)
from backend.agent.factory import build_agent, build_model
from backend.agent.finale import Finale
from backend.agent.guard import apply_guard, desk_status
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
                    "structured_response": None,
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
                finale = _finale_from(result)
                if finale is None:
                    finale = await _finale_from_card(self._settings, ctx.card)
                decided = apply_guard(ctx.card, finale, ctx.catalog_errors)
                _write_decision(ctx.card, decided, mock)
                await _commit_finish(channel, repo, appeal, ctx, result, decided)
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


def _write_decision(card: dict[str, Any], decided: Finale, mock: MockHttp) -> None:
    card.setdefault("decision", {})
    card["decision"].update(
        {
            "outcome": decided.outcome,
            "reason": decided.reason,
            "grounds": decided.grounds,
            "questions": decided.questions,
            "warnings": decided.warnings,
            "reply_draft": decided.reply_draft,
        }
    )
    if decided.outcome in {"create", "update"}:
        try_itsm(mock, card, decided.outcome)
        return
    card["decision"]["ticket_draft"] = None
    card["decision"]["itsm_dry_run"] = None
    card["decision"]["auto_in_prod"] = False


async def _commit_finish(
    channel: RunChannel,
    repo: AppealRepository,
    appeal: Appeal,
    ctx: RunContext,
    result: dict[str, Any],
    decided: Finale,
) -> None:
    appeal.card = ctx.card
    flag_modified(appeal, "card")
    appeal.status = desk_status(decided.outcome)
    appeal.run_status = "idle"
    report = await _persist_report(repo, appeal.id, ctx.card, result.get("persist"))
    await repo.add_event(
        AppealEvent(appeal_id=appeal.id, type="run_finished", card_snapshot=ctx.card)
    )
    await repo.commit()
    await channel.emit({"type": "card_updated", "card": ctx.card})
    if report:
        await channel.emit({"type": "message_final", "text": report})
    await channel.emit(
        {
            "type": "run_finished",
            "run_status": "idle",
            "outcome": decided.outcome,
            "status": appeal.status,
            "auto_in_prod": bool(ctx.card["decision"].get("auto_in_prod")),
        }
    )


async def _persist_report(
    repo: AppealRepository,
    appeal_id: int,
    card: dict[str, Any],
    persist: object,
) -> str | None:
    if persist_has_message_final(persist):
        return None
    report = build_dispatcher_report(card, tool_names=tool_names_from_persist(persist))
    await repo.add_message(
        AppealMessage(appeal_id=appeal_id, author="agent", kind="message", body={"text": report})
    )
    return report


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


async def _finale_from_card(settings: Settings, card: dict[str, Any]) -> Finale | None:
    model = build_model(settings).with_structured_output(Finale)
    payload = (
        "Карточка уже собрана тулами. Верни только Finale, без тулов.\n"
        f"{json.dumps(card, ensure_ascii=False)[:6000]}"
    )
    try:
        raw = await model.ainvoke(payload)
    except Exception:
        logger.exception("finale fallback")
        return None
    if isinstance(raw, Finale):
        return raw
    try:
        return Finale.model_validate(raw)
    except ValidationError:
        return None


def _finale_from(result: dict[str, Any]) -> Finale | None:
    raw = result.get("structured_response")
    if isinstance(raw, Finale):
        return raw
    if raw is None:
        return None
    try:
        return Finale.model_validate(raw)
    except ValidationError:
        return None
