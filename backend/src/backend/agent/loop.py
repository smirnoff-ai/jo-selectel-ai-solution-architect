import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import ValidationError

from backend.agent.finale import Finale

logger = logging.getLogger(__name__)
MAX_STEPS = 8


async def run_tool_loop(
    model: Any,
    tools: list[Any],
    *,
    system_prompt: str,
    user_text: str,
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
            return {"messages": messages, "structured_response": parse_finale(ai)}
        for call in ai.tool_calls:
            name = str(call.get("name") or "")
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
            messages.append(
                ToolMessage(
                    content=content if isinstance(content, str) else json.dumps(content),
                    tool_call_id=str(call.get("id") or name),
                    name=name,
                )
            )
    return {"messages": messages, "structured_response": None}


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
