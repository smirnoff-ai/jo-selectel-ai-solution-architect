from typing import Any

from backend.agent.card_slots import binding_status, slot


def support_clear(card: dict[str, Any], outcome: str) -> bool:
    if binding_status(card, "customer") != "resolved":
        return False
    if binding_status(card, "site") != "resolved":
        return False
    asset = binding_status(card, "asset")
    if asset in {"ambiguous", "not_found"}:
        return False
    if outcome == "update":
        return binding_status(card, "history") == "resolved"
    if outcome == "create":
        return binding_status(card, "history") != "resolved"
    return False


def build_ticket_draft(card: dict[str, Any], outcome: str) -> dict[str, Any] | None:
    if outcome not in {"create", "update"} or not support_clear(card, outcome):
        return None
    priority = (card.get("calculation") or {}).get("priority", {}).get("value") or "medium"
    problem = slot(card, "problem").get("value") or card["intake"]["text"]
    draft: dict[str, Any] = {
        "customer_id": slot(card, "customer")["binding"]["id"],
        "site_id": slot(card, "site")["binding"]["id"],
        "contract_id": (card.get("contract") or {}).get("id"),
        "summary": str(problem)[:240],
        "priority": priority,
    }
    asset_id = slot(card, "asset")["binding"]["id"]
    if asset_id:
        draft["asset_id"] = asset_id
    if outcome == "update":
        draft["ticket_id"] = slot(card, "history")["binding"]["id"]
    return draft
