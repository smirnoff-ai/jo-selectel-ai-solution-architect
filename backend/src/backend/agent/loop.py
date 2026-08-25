import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import ValidationError

from backend.agent.finale import Finale

logger = logging.getLogger(__name__)
MAX_STEPS = 8
OnEvent = Callable[[dict[str, Any]], Awaitable[None]]


async def run_tool_loop(
    model: Any,
    tools: list[Any],
    *,
    system_prompt: str,
    user_text: str,
    on_event: OnEvent | None = None,
) -> dict[str, Any]:
    tool_map = {tool.name: tool for tool in tools}
    bound = model.bind_tools(tools)
    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_text),
    ]
    for _ in range(MAX_STEPS):
        ai = await bound.ainvoke(messages)
        messages.append(ai)
        if not isinstance(ai, AIMessage) or not ai.tool_calls:
            text = _ai_text(ai)
            if text:
                await _emit(on_event, {"type": "message_final", "text": text})
            return {"messages": messages, "structured_response": parse_finale(ai)}
        thought = _ai_thought(ai)
        if thought:
            await _emit(on_event, {"type": "thought", "text": thought})
        for call in ai.tool_calls:
            name = str(call.get("name") or "")
            call_id = str(call.get("id") or name)
            await _emit(
                on_event,
                {"type": "tool_call", "id": call_id, "name": name, "args": call.get("args")},
            )
            tool = tool_map.get(name)
            if tool is None:
                content = json.dumps({"status": "error", "summary": f"нет тула {name}"})
            else:
                try:
                    content = tool.invoke(_coerce_args(call.get("args") or {}))
                except Exception as exc:
                    logger.exception("tool %s", name)
                    content = json.dumps(
                        {
                            "status": "error",
                            "summary": f"{name}: {exc}",
                            "next_actions": ["передать объекты, не JSON-строки"],
                        },
                        ensure_ascii=False,
                    )
            payload = content if isinstance(content, str) else json.dumps(content)
            messages.append(ToolMessage(content=payload, tool_call_id=call_id, name=name))
            parsed = _parse_tool(payload)
            await _emit(on_event, {"type": "tool_result", "id": call_id, "name": name, **parsed})
    return {"messages": messages, "structured_response": None}


async def _emit(on_event: OnEvent | None, payload: dict[str, Any]) -> None:
    if on_event is not None:
        await on_event(payload)


def _ai_thought(message: AIMessage) -> str | None:
    extra = message.additional_kwargs or {}
    for key in ("reasoning_content", "reasoning"):
        value = extra.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _ai_text(message: AIMessage) -> str:
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


def _coerce_args(args: object) -> dict[str, Any]:
    if not isinstance(args, dict):
        return {}
    out: dict[str, Any] = {}
    for key, value in args.items():
        if isinstance(value, str) and value[:1] in "{[":
            try:
                out[key] = json.loads(value)
                continue
            except json.JSONDecodeError:
                pass
        out[key] = value
    return out


def parse_finale(message: BaseMessage) -> Finale | None:
    text = message.content if isinstance(message.content, str) else str(message.content)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return Finale.model_validate(json.loads(text[start : end + 1]))
    except (json.JSONDecodeError, ValidationError):
        logger.info("finale parse missed")
        return None
