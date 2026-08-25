import json
from typing import Annotated

from langchain.tools import tool

from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def get_contract(
    site_id: Annotated[
        str | None,
        "Идентификатор уже выбранной площадки. Обязателен, с карточки сам не подставится",
    ] = None,
) -> str:
    """Возвращает условия договора площадки.

    Карточку не меняет и сроки не считает. Без идентификатора площадки не вызывай.
    Нет договора — refuse_auto, покрытие не выдумывай. Код срока и окно нужны calculate.
    """
    ctx = get_run_context()
    if not site_id:
        return json.dumps(
            tool_payload(
                status="error",
                summary="Нужен идентификатор площадки",
                next_actions=["сначала найти одну площадку и передать site_id из result.items"],
            ),
            ensure_ascii=False,
        )
    try:
        status, body = ctx.mock.get("/contracts/v1/contracts", {"site_id": site_id})
    except OSError as exc:
        count = ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"contracts недоступен: {exc}",
                next_actions=["повторить один раз" if count < 2 else "финал dispatch"],
            ),
            ensure_ascii=False,
        )
    if status >= 400:
        count = ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary=f"contracts {status}",
                next_actions=["финал dispatch"] if count >= 2 else ["проверить site_id"],
                result={"body": body},
            ),
            ensure_ascii=False,
        )
    items = list(body.get("items") or []) if isinstance(body, dict) else []
    ctx.remember_ids(items)
    if len(items) > 1:
        ctx.note_error("contracts")
        return json.dumps(
            tool_payload(
                status="error",
                summary="На площадку несколько договоров — выбрать нельзя",
                next_actions=["финал dispatch"],
                result={"items": items},
            ),
            ensure_ascii=False,
        )
    if not items:
        return json.dumps(
            tool_payload(
                status="warning",
                summary="Договора на площадку нет",
                next_actions=[
                    "запиши contract.status=not_found через update_card",
                    "исход refuse_auto",
                ],
                result={"items": items},
            ),
            ensure_ascii=False,
        )
    row = items[0]
    return json.dumps(
        tool_payload(
            status="success",
            summary=f"Договор {row.get('contract_id')}",
            next_actions=[
                "запиши договор через update_card",
                "затем calculate с кодом срока, окном и поясом площадки",
            ],
            result={"items": items},
        ),
        ensure_ascii=False,
    )
