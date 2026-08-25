from typing import Any

from backend.agent.mock_http import MockHttp
from backend.agent.ticket_draft import build_ticket_draft


def try_itsm(mock: MockHttp, card: dict[str, Any], outcome: str) -> dict[str, Any] | None:
    draft = build_ticket_draft(card, outcome)
    card["decision"]["ticket_draft"] = draft
    if draft is None:
        card["decision"]["itsm_dry_run"] = None
        card["decision"]["auto_in_prod"] = False
        return None

    payload = {key: value for key, value in draft.items() if key != "ticket_id"}
    if outcome == "update":
        ticket_id = draft["ticket_id"]
        status, body = mock.patch(
            f"/itsm/v1/tickets/{ticket_id}",
            {"summary": payload["summary"], "priority": payload["priority"]},
        )
    else:
        status, body = mock.post("/itsm/v1/tickets", payload)

    if not isinstance(body, dict):
        body = {"detail": str(body), "accepted": False}
    if status >= 400:
        body = {**body, "accepted": False, "persisted": False}
    card["decision"]["itsm_dry_run"] = body
    card["decision"]["auto_in_prod"] = bool(body.get("accepted"))
    return body
