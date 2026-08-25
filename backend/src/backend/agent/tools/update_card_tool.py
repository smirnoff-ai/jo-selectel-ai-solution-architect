import json
from typing import Any

from langchain.tools import tool
from pydantic import ValidationError

from backend.agent.patch_merge import MergeRejectedError, merge_update
from backend.agent.run_context import get_run_context
from backend.agent.schemas.update_card import UpdateCardInput
from backend.agent.tool_payload import tool_payload


@tool(args_schema=UpdateCardInput)
def update_card(
    customer: dict[str, Any] | None = None,
    site: dict[str, Any] | None = None,
    asset: dict[str, Any] | None = None,
    history: dict[str, Any] | None = None,
    problem: dict[str, Any] | None = None,
    symptoms: dict[str, Any] | None = None,
    desired_deadline: dict[str, Any] | None = None,
    backup: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
    calculation: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
) -> str:
    """Записывает на карточку любые её поля и возвращает полный документ.

    Поиски карточку не меняют — после справочника вызови этот инструмент.
    Идентификатор «с потолка» будет отклонён. Опущенное поле не затирается.
    """
    ctx = get_run_context()
    raw = {
        "customer": customer,
        "site": site,
        "asset": asset,
        "history": history,
        "problem": problem,
        "symptoms": symptoms,
        "desired_deadline": desired_deadline,
        "backup": backup,
        "contract": contract,
        "calculation": calculation,
        "decision": decision,
    }
    try:
        patch = UpdateCardInput.model_validate({key: value for key, value in raw.items() if value})
        updated = merge_update(
            ctx.card,
            patch,
            seen_ids=ctx.seen_ids,
            last_calculation=ctx.last_calculation,
        )
    except (ValidationError, MergeRejectedError) as exc:
        return json.dumps(
            tool_payload(
                status="error",
                summary="update_card отклонён",
                next_actions=[
                    "исправить аргументы: цитата для факта, id только из поиска",
                ],
                result={"detail": str(exc)},
            ),
            ensure_ascii=False,
        )
    ctx.snapshot()
    return json.dumps(
        tool_payload(
            status="success",
            summary=f"Записаны поля: {', '.join(updated)}",
            next_actions=[
                "посмотри result.card: дозаполни пустое поиском или переходи к расчёту и решению",
            ],
            artifacts={"updated": updated},
            result={"card": ctx.card},
        ),
        ensure_ascii=False,
    )
