from typing import Annotated

from langchain.tools import tool

from backend.agent.catalog_call import catalog_get
from backend.agent.run_context import get_run_context


@tool
def search_sites(
    q: Annotated[
        str | None,
        "Свободный запрос: название организации или адрес, не имя человека",
    ] = None,
    customer_id: Annotated[str | None, "Идентификатор клиента из предыдущего ответа поиска"] = None,
    site_id: Annotated[str | None, "Идентификатор площадки, если уже известен из поиска"] = None,
    customer_name: Annotated[str | None, "Название организации-клиента"] = None,
    address: Annotated[str | None, "Адрес или часть адреса объекта"] = None,
    timezone: Annotated[str | None, "Часовой пояс площадки, только если он явно назван"] = None,
) -> str:
    """Ищет клиента и площадки в справочнике клиентов.

    Карточку не меняет. Вернёт записи в result.items. Ноль, одну или несколько
    записей ты сам переносишь на карточку через update_card. Можно вызвать
    снова с другими фильтрами. Имя человека из подписи — плохой фильтр.
    """
    ctx = get_run_context()
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
        empty_summary="Площадок не нашли",
        found_summary=lambda items: f"Площадок: {len(items)}",
        next_on_empty=["уточнить организацию или адрес и повторить поиск, затем update_card"],
        next_on_found=[
            "запиши клиента и площадку через update_card по числу записей в result.items",
            "если в письме назвали установку — сразу search_assets, даже когда площадок несколько",
        ],
    )
