import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.errors import GraphRecursionError

logger = logging.getLogger(__name__)

OnEvent = Callable[[dict[str, Any]], Awaitable[None]]


def message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "reasoning":
                    continue
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif block is not None:
                parts.append(str(block))
        return "".join(parts)
    return "" if content is None else str(content)


async def map_agent_stream(stream: Any, on_event: OnEvent) -> dict[str, Any]:
    persist: list[dict[str, Any]] = []
    usage: dict[str, int] = {}
    await _consume(stream, on_event, persist, usage)
    messages_out = await _final_messages(stream)
    if usage:
        await on_event({"type": "context_usage", **usage})
    return {
        "messages": messages_out,
        "persist": persist,
    }


async def _consume(
    stream: Any,
    on_event: OnEvent,
    persist: list[dict[str, Any]],
    usage: dict[str, int],
) -> None:
    try:
        await asyncio.gather(
            _messages(stream, on_event, persist, usage),
            _tools(stream, on_event, persist),
        )
    except GraphRecursionError:
        logger.exception("agent stream hit recursion_limit")


async def _messages(
    stream: Any,
    on_event: OnEvent,
    persist: list[dict[str, Any]],
    usage: dict[str, int],
) -> None:
    async for message in stream.messages:
        thought_parts: list[str] = []
        async for delta in message.reasoning:
            if not delta:
                continue
            thought_parts.append(delta)
            await on_event({"type": "thought", "delta": delta})
        thought = "".join(thought_parts).strip()
        if thought:
            persist.append({"type": "thought", "text": thought})
        text_parts: list[str] = []
        async for delta in message.text:
            if not delta:
                continue
            text_parts.append(delta)
            await on_event({"type": "message_delta", "delta": delta})
        output = await message.output
        if isinstance(output, AIMessage):
            _merge_usage(usage, getattr(output, "usage_metadata", None))
            text = "".join(text_parts) or message_text(output.content)
            if text and not output.tool_calls:
                event = {"type": "message_final", "text": text}
                persist.append(event)
                await on_event(event)


async def _tools(stream: Any, on_event: OnEvent, persist: list[dict[str, Any]]) -> None:
    async for call in stream.tool_calls:
        call_id = str(getattr(call, "tool_call_id", "") or "")
        name = str(getattr(call, "tool_name", "") or "")
        args = _tool_args(getattr(call, "input", None))
        started = {"type": "tool_call", "id": call_id, "name": name, "args": args}
        persist.append(started)
        await on_event(started)
        async for _delta in call.output_deltas:
            pass
        result = _tool_result(getattr(call, "output", None), getattr(call, "error", None))
        finished = {"type": "tool_result", "id": call_id, "name": name, **result}
        persist.append(finished)
        await on_event(finished)


async def _final_messages(stream: Any) -> list[Any]:
    try:
        final_state = await stream.output()
    except Exception:
        logger.exception("agent stream output")
        return []
    if isinstance(final_state, dict):
        return list(final_state.get("messages") or [])
    return []


def _tool_args(raw: object) -> dict[str, Any]:
    if isinstance(raw, dict):
        if isinstance(raw.get("args"), dict):
            return raw["args"]
        if isinstance(raw.get("tool_call"), dict):
            inner = raw["tool_call"]
            if isinstance(inner.get("args"), dict):
                return inner["args"]
        return raw
    return {}


def _tool_result(output: object, error: object) -> dict[str, Any]:
    if error:
        return {"status": "error", "summary": str(error)}
    content: object = output
    if isinstance(output, BaseMessage):
        content = output.content
    return _parse_tool(content)


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
    return {"summary": str(content)} if content is not None else {"summary": ""}


def _merge_usage(acc: dict[str, int], raw: object) -> None:
    if raw is None:
        return
    if isinstance(raw, dict):
        data = raw
    else:
        data = {
            "input_tokens": getattr(raw, "input_tokens", None),
            "output_tokens": getattr(raw, "output_tokens", None),
            "total_tokens": getattr(raw, "total_tokens", None),
        }
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        value = data.get(key)
        if isinstance(value, int):
            acc[key] = acc.get(key, 0) + value
