import json
from typing import Annotated

from langchain.tools import tool

from backend.agent.catalog_call import catalog_get, drop_empty
from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def search_tickets(
    asset_id: Annotated[str | None, "Идентификатор уже выбранного оборудования, обязателен"] = None,
    customer_id: Annotated[str | None, "Идентификатор клиента, если уже известен"] = None,
    site_id: Annotated[str | None, "Идентификатор площадки, если уже известен"] = None,
    contract_id: Annotated[str | None, "Идентификатор договора, если уже известен"] = None,
    status: Annotated[str | None, "Статус заявок, по умолчанию open"] = "open",
) -> str:
    """Ищет открытые заявки.

    Карточку не меняет. Нужен явный идентификатор оборудования из поиска.
    Одна открытая заявка по тому же оборудованию — ветка обновления.
    """
    ctx = get_run_context()
    if not asset_id:
        return json.dumps(
            tool_payload(
                status="error",
                summary="Заявки ищем только по однозначно выбранному оборудованию",
                next_actions=["сначала search_assets, затем передай asset_id из result.items"],
            ),
            ensure_ascii=False,
        )
    return catalog_get(
        ctx,
        catalog="itsm",
        path="/itsm/v1/tickets",
        params=drop_empty(
            {
                "customer_id": customer_id,
                "site_id": site_id,
                "asset_id": asset_id,
                "contract_id": contract_id,
                "status": status,
            }
        ),
        empty_summary="Открытых заявок нет",
        found_summary=lambda items: f"Открытых заявок: {len(items)}",
        next_on_empty=["запиши историю при необходимости и переходи к договору и расчёту"],
        next_on_found=[
            "запиши заявку через update_card: одна открытая — resolved, несколько — не выбирай",
            "приоритет заявки запомни для calculate",
        ],
    )
