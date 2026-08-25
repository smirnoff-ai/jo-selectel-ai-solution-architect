from langchain.tools import tool

from backend.agent.bindings import apply_assets
from backend.agent.calculation import stash_asset_criticality
from backend.agent.catalog_call import catalog_get
from backend.agent.run_context import get_run_context


@tool
def search_assets(
    q: str | None = None,
    asset_id: str | None = None,
    site_id: str | None = None,
    local_code: str | None = None,
    asset_type: str | None = None,
    criticality: str | None = None,
) -> str:
    """Поиск оборудования в EAM. Два ХУ-17 не выбирать."""
    ctx = get_run_context()

    def on_items(card: dict, items: list[dict]) -> list[str]:
        stash_asset_criticality(card, items)
        return apply_assets(card, items)

    return catalog_get(
        ctx,
        catalog="eam",
        path="/eam/v1/assets",
        params={
            "q": q,
            "asset_id": asset_id,
            "site_id": site_id,
            "local_code": local_code,
            "asset_type": asset_type,
            "criticality": criticality,
        },
        on_items=on_items,
        empty_summary="Активов не нашли",
        found_summary=lambda items: f"Активов: {len(items)}",
        next_on_empty=["не заводить заявку на площадку без актива, если актив называли"],
        next_on_found=["если несколько — clarify; если один — search_tickets и get_contract"],
    )
