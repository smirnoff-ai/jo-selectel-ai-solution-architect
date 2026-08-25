import json

from langchain.tools import tool
from pydantic import ValidationError

from backend.agent.patch_merge import merge_patch
from backend.agent.run_context import get_run_context
from backend.agent.schemas.patch_facts import PatchFactsInput
from backend.agent.tool_payload import tool_payload


@tool(args_schema=PatchFactsInput)
def patch_facts(
    customer: dict | None = None,
    site: dict | None = None,
    asset: dict | None = None,
    history: dict | None = None,
    problem: dict | None = None,
    symptoms: dict | None = None,
    desired_deadline: dict | None = None,
    backup: dict | None = None,
) -> str:
    """Записать упоминания и смыслы. Binding не принимает. Нужен хотя бы один слот."""
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
    }
    try:
        patch = PatchFactsInput.model_validate({key: value for key, value in raw.items() if value})
    except ValidationError as exc:
        return json.dumps(
            tool_payload(
                status="error",
                summary="patch_facts отклонён схемой",
                next_actions=["исправить аргументы, binding не передавать"],
                result={"detail": str(exc)},
            ),
            ensure_ascii=False,
        )
    updated = merge_patch(ctx.card, patch)
    ctx.snapshot()
    return json.dumps(
        tool_payload(
            status="success",
            summary=f"Записаны слоты: {', '.join(updated)}",
            next_actions=["искать площадки или активы по упоминаниям"],
            artifacts={"updated": updated},
        ),
        ensure_ascii=False,
    )
