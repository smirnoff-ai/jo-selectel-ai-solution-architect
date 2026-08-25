import json
import re
from typing import Annotated

from langchain.tools import tool

from backend.agent.catalog_call import catalog_get
from backend.agent.run_context import get_run_context
from backend.agent.tool_payload import tool_payload


@tool
def search_assets(
    q: Annotated[
        str | None,
        "Код, число или тип установки. Разговорное «семнадцатая» лучше передать как число или код",
    ] = None,
    asset_id: Annotated[str | None, "Идентификатор актива из предыдущего ответа поиска"] = None,
    site_id: Annotated[
        str | None,
        "Идентификатор площадки, если хочешь сузить поиск. С карточки сам не подставится",
    ] = None,
    local_code: Annotated[str | None, "Внутренний код установки на площадке"] = None,
    asset_type: Annotated[str | None, "Тип оборудования, если кода нет"] = None,
    criticality: Annotated[str | None, "Критичность, только если она явно названа"] = None,
) -> str:
    """Ищет оборудование в реестре.

    Карточку не меняет. Несколько совпадений с одним кодом — не выбирай,
    запиши неоднозначность через update_card и уточни у диспетчера.
    """
    ctx = get_run_context()
    query = _asset_query(q)
    if not any((query, asset_id, local_code, asset_type)):
        return json.dumps(
            tool_payload(
                status="error",
                summary="Нужен код, число или тип установки",
                next_actions=["передать q или local_code из письма, не искать все активы площадки"],
            ),
            ensure_ascii=False,
        )
    return catalog_get(
        ctx,
        catalog="eam",
        path="/eam/v1/assets",
        params={
            "q": query,
            "asset_id": asset_id,
            "site_id": site_id,
            "local_code": local_code,
            "asset_type": asset_type,
            "criticality": criticality,
        },
        empty_summary="Активов не нашли",
        found_summary=lambda items: f"Активов: {len(items)}",
        next_on_empty=[
            "если искали разговорную форму — повторить q числом или кодом из письма",
            "запиши not_found через update_card; заявку на площадку без актива не предлагай",
        ],
        next_on_found=[
            "запиши оборудование через update_card: одна запись — resolved, несколько — ambiguous",
            "критичность из result запомни для calculate",
        ],
    )


_ORDINAL_Q = re.compile(
    r"^(\d+)\s*-?(?:я|й|е|ая|ое|ый|ую)?$",
    flags=re.IGNORECASE,
)


def _asset_query(q: str | None) -> str | None:
    if q is None:
        return None
    match = _ORDINAL_Q.fullmatch(q.strip())
    if match:
        return match.group(1)
    return q
