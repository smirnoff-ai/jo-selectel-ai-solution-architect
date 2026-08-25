from typing import Any, Literal

Status = Literal["success", "warning", "error"]


def tool_payload(
    *,
    status: Status,
    summary: str,
    next_actions: list[str],
    artifacts: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "next_actions": next_actions,
        "artifacts": artifacts or {},
        "result": result or {},
    }
