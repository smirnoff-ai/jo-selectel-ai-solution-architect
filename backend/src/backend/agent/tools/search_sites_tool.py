from langchain.tools import tool

from backend.agent.bindings import apply_sites
from backend.agent.calculation import stash_site_timezone
from backend.agent.catalog_call import catalog_get
from backend.agent.run_context import get_run_context


@tool
def search_sites(
    q: str | None = None,
    customer_id: str | None = None,
    site_id: str | None = None,
    customer_name: str | None = None,
    address: str | None = None,
    timezone: str | None = None,
) -> str:
    """Поиск клиента и площадок в CRM. Привязку 0/1/N пишет код."""
    ctx = get_run_context()

    def on_items(card: dict, items: list[dict]) -> list[str]:
        stash_site_timezone(card, items)
        return apply_sites(card, items, query=q or customer_name or address)

    return catalog_get(
        ctx,
        catalog="crm",
        path="/crm/v1/sites",
        params={
            "q": q,
            "customer_id": customer_id,
            "site_id": site_id,
            "customer_name": customer_name,
            "address": address,
            "timezone": timezone,
        },
        on_items=on_items,
        empty_summary="Площадок не нашли",
        found_summary=lambda items: f"Площадок: {len(items)}",
        next_on_empty=["уточнить организацию или адрес, не имя человека"],
        next_on_found=["если объект resolved — get_contract и search_assets"],
    )
