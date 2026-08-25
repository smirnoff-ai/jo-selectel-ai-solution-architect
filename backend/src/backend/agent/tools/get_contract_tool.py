import json

from langchain.tools import tool

from backend.agent.bindings import apply_contract
from backend.agent.calculation import recalc
from backend.agent.card_slots import binding_status, slot
from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def get_contract(site_id: str | None = None) -> str:
    """Договор площадки. Площадка должна быть resolved."""
    ctx = get_run_context()
    site_resolved = binding_status(ctx.card, "site") == "resolved"
    resolved = slot(ctx.card, "site")["binding"]["id"] if site_resolved else None
    ident = site_id or resolved
    if not ident:
        return json.dumps(
            tool_payload(
                status="error",
                summary="Площадка не resolved — договор не спрашиваем",
                next_actions=["сначала однозначный объект"],
            ),
            ensure_ascii=False,
        )
    try:
        status, body = ctx.mock.get("/contracts/v1/contracts", {"site_id": ident})
    except OSError as exc:
        count = ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"contracts недоступен: {exc}",
                next_actions=["повторить один раз" if count < 2 else "исход dispatch"],
            ),
            ensure_ascii=False,
        )
    if status >= 400:
        count = ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"contracts {status}",
                next_actions=["исход dispatch"] if count >= 2 else ["проверить site_id"],
                result={"body": body},
            ),
            ensure_ascii=False,
        )
    items = list(body.get("items") or []) if isinstance(body, dict) else []
    applied = apply_contract(ctx.card, items)
    if applied == "many":
        ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary="На площадку несколько договоров — пилот не выбирает",
                next_actions=["исход dispatch"],
                result={"items": items},
            ),
            ensure_ascii=False,
        )
    recalc(ctx.card)
    ctx.snapshot()
    if applied == "not_found":
        return json.dumps(
            tool_payload(
                status="warning",
                summary="Договора на площадку нет",
                next_actions=["исход refuse_auto, Gold не выдумывать"],
                artifacts={"updated": ["contract"]},
                result={"items": items},
            ),
            ensure_ascii=False,
        )
    return json.dumps(
        tool_payload(
            status="success",
            summary=f"Договор {ctx.card['contract']['id']}",
            next_actions=["если опора ясна — финал create или update"],
            artifacts={"updated": ["contract", "calculation"]},
            result={"items": items},
        ),
        ensure_ascii=False,
    )
