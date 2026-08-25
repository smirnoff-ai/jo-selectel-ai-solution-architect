import json
from typing import Any

from langchain.tools import tool
from pydantic import ValidationError

from backend.agent.calculation import compute_calculation
from backend.agent.run_context import get_run_context
from backend.agent.schemas.calculate import CalculateInput
from backend.agent.tool_payload import tool_payload


@tool(args_schema=CalculateInput)
def calculate(
    asset_criticality: str | None = None,
    symptoms_text: str = "",
    open_ticket_priority: str | None = None,
    response_sla: str | None = None,
    service_window: str | None = None,
    timezone: str | None = None,
) -> str:
    """Считает приоритет, срок ответа и дедлайн по регламенту.

    Карточку не читает и не пишет. Передай аргументы из ответов поисков и договора.
    Время получения обращения возьмётся само. Результат запиши через update_card.
    """
    ctx = get_run_context()
    raw: dict[str, Any] = {
        "asset_criticality": asset_criticality,
        "symptoms_text": symptoms_text,
        "open_ticket_priority": open_ticket_priority,
        "response_sla": response_sla,
        "service_window": service_window,
        "timezone": timezone,
    }
    try:
        args = CalculateInput.model_validate(raw)
    except ValidationError as exc:
        return json.dumps(
            tool_payload(
                status="error",
                summary="calculate отклонён схемой",
                next_actions=["передать только известные коды из ответов справочников"],
                result={"detail": str(exc)},
            ),
            ensure_ascii=False,
        )
    block = compute_calculation(
        received_at=ctx.received_at,
        timezone=args.timezone,
        response_sla=args.response_sla,
        service_window=args.service_window,
        asset_criticality=args.asset_criticality,
        symptoms_text=args.symptoms_text,
        open_ticket_priority=args.open_ticket_priority,
    )
    ctx.last_calculation = block
    missing = list(block["sla"]["missing"]) + list(block["deadline"]["missing"])
    return json.dumps(
        tool_payload(
            status="success" if block["status"] == "computed" else "warning",
            summary=(
                f"Расчёт {block['status']}: приоритет {block['priority']['value']}"
                + (f", не хватает {', '.join(missing)}" if missing else "")
            ),
            next_actions=["запиши result.calculation в карточку через update_card"],
            result={"calculation": block},
        ),
        ensure_ascii=False,
    )
