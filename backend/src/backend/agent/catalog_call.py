import json
from collections.abc import Callable
from typing import Any

from backend.agent.calculation import recalc
from backend.agent.run_context import RunContext
from backend.agent.tool_payload import tool_payload


def drop_empty(params: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in params.items() if value not in (None, "")}


def catalog_get(
    ctx: RunContext,
    *,
    catalog: str,
    path: str,
    params: dict[str, Any],
    on_items: Callable[[dict[str, Any], list[dict[str, Any]]], list[str]],
    empty_summary: str,
    found_summary: Callable[[list[dict[str, Any]]], str],
    next_on_empty: list[str],
    next_on_found: list[str],
) -> str:
    clean = drop_empty(params)
    if not clean:
        return json.dumps(
            tool_payload(
                status="error",
                summary="Нужен хотя бы один фильтр",
                next_actions=["передать q или id"],
            ),
            ensure_ascii=False,
        )
    try:
        status, body = ctx.mock.get(path, clean)
    except OSError as exc:
        count = ctx.note_error(catalog)
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"{catalog} недоступен: {exc}",
                next_actions=["повторить один раз" if count < 2 else "исход dispatch"],
            ),
            ensure_ascii=False,
        )
    if status >= 400:
        count = ctx.note_error(catalog)
        detail = body.get("detail") if isinstance(body, dict) else str(body)
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"{catalog} {status}: {detail}",
                next_actions=["повторить с другими фильтрами" if count < 2 else "исход dispatch"],
                result={"status_code": status, "body": body},
            ),
            ensure_ascii=False,
        )
    items = list(body.get("items") or []) if isinstance(body, dict) else []
    updated = on_items(ctx.card, items)
    recalc(ctx.card)
    ctx.snapshot()
    if not items:
        return json.dumps(
            tool_payload(
                status="warning",
                summary=empty_summary,
                next_actions=next_on_empty,
                artifacts={"updated": updated},
                result={"items": items, "query": clean},
            ),
            ensure_ascii=False,
        )
    return json.dumps(
        tool_payload(
            status="success",
            summary=found_summary(items),
            next_actions=next_on_found,
            artifacts={"updated": updated},
            result={"items": items, "query": clean},
        ),
        ensure_ascii=False,
    )
