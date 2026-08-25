import json

from langchain.tools import tool

from backend.agent.bindings import apply_tickets
from backend.agent.calculation import stash_ticket_priority
from backend.agent.card_slots import binding_status, slot
from backend.agent.catalog_call import catalog_get, drop_empty
from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def search_tickets(
    customer_id: str | None = None,
    site_id: str | None = None,
    asset_id: str | None = None,
    contract_id: str | None = None,
    status: str | None = "open",
) -> str:
    """Открытые заявки ITSM. Без фильтра подставляет resolved слоты."""
    ctx = get_run_context()
    params = drop_empty(
        {
            "customer_id": customer_id or _resolved(ctx.card, "customer"),
            "site_id": site_id or _resolved(ctx.card, "site"),
            "asset_id": asset_id or _resolved(ctx.card, "asset"),
            "contract_id": contract_id,
            "status": status,
        }
    )
    if not any(params.get(key) for key in ("customer_id", "site_id", "asset_id", "contract_id")):
        return json.dumps(
            tool_payload(
                status="error",
                summary="Нечего подставить в поиск заявок",
                next_actions=["сначала resolved клиент, площадка или актив"],
            ),
            ensure_ascii=False,
        )

    def on_items(card: dict, items: list[dict]) -> list[str]:
        stash_ticket_priority(card, items)
        return apply_tickets(card, items)

    return catalog_get(
        ctx,
        catalog="itsm",
        path="/itsm/v1/tickets",
        params=params,
        on_items=on_items,
        empty_summary="Открытых заявок нет",
        found_summary=lambda items: f"Открытых заявок: {len(items)}",
        next_on_empty=["ветка create, если опора ясна"],
        next_on_found=["если одна — update; если несколько — не выбирать"],
    )


def _resolved(card: dict, name: str) -> str | None:
    if binding_status(card, name) != "resolved":
        return None
    ident = slot(card, name)["binding"]["id"]
    return str(ident) if ident else None
