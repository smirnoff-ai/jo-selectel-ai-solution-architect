import json
from typing import Annotated

from langchain.tools import tool

from backend.agent.catalog_call import catalog_get, drop_empty
from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def search_tickets(
    asset_id: Annotated[str | None, "Идентификатор оборудования, если уже известен"] = None,
    customer_id: Annotated[str | None, "Идентификатор клиента, если уже известен"] = None,
    site_id: Annotated[str | None, "Идентификатор площадки, если уже известен"] = None,
    contract_id: Annotated[str | None, "Идентификатор договора, если уже известен"] = None,
    status: Annotated[str | None, "Статус заявок, по умолчанию open"] = "open",
) -> str:
    """Ищет заявки.

    Карточку не меняет. Нужен хотя бы один устойчивый фильтр: customer_id,
    site_id, asset_id или contract_id. В result.items — полные поля заявки:
    ticket_id, customer_id, site_id, asset_id, contract_id, status, priority,
    summary, created_at, updated_at. Одна открытая по тому же оборудованию —
    ветка обновления.
    """
    ctx = get_run_context()
    identity = drop_empty(
        {
            "customer_id": customer_id,
            "site_id": site_id,
            "asset_id": asset_id,
            "contract_id": contract_id,
        }
    )
    if not identity:
        return json.dumps(
            tool_payload(
                status="error",
                summary="Заявки ищем по клиенту, площадке, оборудованию или договору",
                next_actions=[
                    "передай customer_id, site_id, asset_id или contract_id из ответа поиска"
                ],
            ),
            ensure_ascii=False,
        )
    return catalog_get(
        ctx,
        catalog="itsm",
        path="/itsm/v1/tickets",
        params=drop_empty({**identity, "status": status}),
        empty_summary="Открытых заявок нет",
        found_summary=lambda items: f"Открытых заявок: {len(items)}",
        next_on_empty=["запиши историю при необходимости и переходи к договору и расчёту"],
        next_on_found=[
            "history resolved только если ticket.asset_id совпал с уже resolved оборудованием",
            "если актив ambiguous или not_found — заявку не пришивай",
            "приоритет заявки запомни для calculate",
        ],
    )
