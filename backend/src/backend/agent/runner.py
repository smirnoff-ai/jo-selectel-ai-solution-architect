import asyncio
import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from backend.agent.factory import TOOLS, build_model
from backend.agent.finale import Finale
from backend.agent.guard import apply_guard, desk_status
from backend.agent.itsm_tryon import try_itsm
from backend.agent.langfuse_trace import make_langfuse
from backend.agent.loop import run_tool_loop
from backend.agent.mock_http import MockHttp
from backend.agent.run_context import RunContext, clear_run_context, set_run_context
from backend.agent.run_hub import RunChannel, RunHub
from backend.agent.system_prompt import load_system_prompt
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
        self._model = None

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
                ctx = RunContext(appeal_id=appeal_id, card=appeal.card, mock=mock)
                set_run_context(ctx)
                result = await asyncio.wait_for(
                    self._invoke(appeal, reply_text, channel, ctx),
                    timeout=self._settings.agent_timeout_seconds,
                )
                await self._emit_trace(channel, repo, appeal, result, ctx)
                finale = _finale_from(result)
                decided = apply_guard(ctx.card, finale, ctx.catalog_errors)
                ctx.card.setdefault("decision", {})
                ctx.card["decision"].update(
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
                    try_itsm(mock, ctx.card, decided.outcome)
                else:
                    ctx.card["decision"]["ticket_draft"] = None
                    ctx.card["decision"]["itsm_dry_run"] = None
                    ctx.card["decision"]["auto_in_prod"] = False
                appeal.card = ctx.card
                flag_modified(appeal, "card")
                appeal.status = desk_status(decided.outcome)
                appeal.run_status = "idle"
                await repo.add_event(
                    AppealEvent(
                        appeal_id=appeal.id,
                        type="run_finished",
                        card_snapshot=ctx.card,
                    )
                )
                await repo.commit()
                await channel.emit({"type": "card_updated", "card": ctx.card})
                await channel.emit(
                    {
                        "type": "run_finished",
                        "run_status": "idle",
                        "outcome": decided.outcome,
                        "status": appeal.status,
                        "auto_in_prod": bool(ctx.card["decision"].get("auto_in_prod")),
                    }
                )
        except TimeoutError:
            logger.exception("agent timeout")
            await self._fail(appeal_id, channel, "Таймаут прогона")
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
        if self._model is None:
            self._model = build_model(self._settings)
        lf = make_langfuse(self._settings)
        trace = None
        if lf is not None:
            try:
                trace = lf.trace(
                    name="reflex-appeal",
                    session_id=str(appeal.id),
                    metadata={"appeal_id": appeal.id},
                    input={"appeal_id": appeal.id},
                )
            except Exception:
                logger.exception("langfuse trace")
        try:

            async def on_event(payload: dict[str, Any]) -> None:
                await channel.emit(payload)
                if payload.get("type") == "tool_result" and ctx.snapshots:
                    await channel.emit({"type": "card_updated", "card": ctx.snapshots[-1]})

            return await run_tool_loop(
                self._model,
                TOOLS,
                system_prompt=load_system_prompt(),
                user_text=build_user_message(appeal, reply_text),
                on_event=on_event,
            )
        finally:
            if trace is not None:
                try:
                    trace.update(output={"appeal_id": appeal.id})
                except Exception:
                    logger.exception("langfuse update")
            if lf is not None:
                try:
                    lf.flush()
                except Exception:
                    logger.exception("langfuse flush")

    async def _emit_trace(
        self,
        channel: RunChannel,
        repo: AppealRepository,
        appeal: Appeal,
        result: dict[str, Any],
        _ctx: RunContext,
    ) -> None:
        for message in result.get("messages") or []:
            if not isinstance(message, BaseMessage) or isinstance(message, HumanMessage):
                continue
            if isinstance(message, AIMessage):
                thought = _thought(message)
                if thought:
                    await _note(
                        channel,
                        repo,
                        appeal.id,
                        "thought",
                        {"text": thought},
                        emit=False,
                    )
                for call in message.tool_calls or []:
                    await _note(
                        channel,
                        repo,
                        appeal.id,
                        "tool_call",
                        {"id": call.get("id"), "name": call.get("name"), "args": call.get("args")},
                        emit=False,
                    )
                text = _text(message)
                if text and not message.tool_calls:
                    await _note(
                        channel,
                        repo,
                        appeal.id,
                        "message",
                        {"text": text},
                        event="message_final",
                        emit=False,
                    )
            elif isinstance(message, ToolMessage):
                payload = _parse_tool(message.content)
                await _note(
                    channel,
                    repo,
                    appeal.id,
                    "tool_result",
                    {"id": message.tool_call_id, "name": message.name, **payload},
                    emit=False,
                )

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


def _thought(message: AIMessage) -> str | None:
    extra = message.additional_kwargs or {}
    for key in ("reasoning_content", "reasoning"):
        value = extra.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block) for block in content
        )
    return ""


def _parse_tool(content: object) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {"summary": content}
        if isinstance(parsed, dict):
            return parsed
    return {"summary": str(content)}
