from typing import Any

from backend.agent.card_slots import binding_status, slot
from backend.agent.finale import Finale

OUTCOME_STATUS = {
    "create": "done",
    "update": "done",
    "clarify": "clarify",
    "dispatch": "dispatch",
    "approve": "approve",
    "refuse_auto": "dispatch",
}


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


def apply_guard(
    card: dict[str, Any],
    finale: Finale | None,
    catalog_errors: dict[str, int],
) -> Finale:
    texts = finale or Finale(outcome="dispatch", reason="Модель не вернула финал")
    if any(count >= 2 for count in catalog_errors.values()):
        return texts.model_copy(update={"outcome": "dispatch", "grounds": ["catalog_errors"]})

    customer = binding_status(card, "customer")
    site = binding_status(card, "site")
    asset = binding_status(card, "asset")
    history = binding_status(card, "history")
    contract_status = (card.get("contract") or {}).get("status")

    if customer != "resolved" or site != "resolved":
        return texts.model_copy(
            update={"outcome": "clarify", "grounds": ["facts.customer", "facts.site"]}
        )
    if asset in {"ambiguous", "not_found"}:
        return texts.model_copy(update={"outcome": "clarify", "grounds": ["facts.asset.binding"]})

    outcome = "update" if history == "resolved" else "create"

    coverage = list((card.get("contract") or {}).get("coverage") or [])
    blob = _blob(card)
    if contract_status == "not_found":
        return texts.model_copy(
            update={"outcome": "refuse_auto", "grounds": ["contract.not_found"]}
        )
    if _wants_repair(blob) and coverage and "repair" not in coverage:
        return texts.model_copy(update={"outcome": "approve", "grounds": ["coverage"]})

    warnings = list(texts.warnings)
    if _wants_today(blob) and (card.get("calculation") or {}).get("sla", {}).get("code") in {
        "next_business_day",
        "4_business_hours",
    }:
        warnings.append(
            {
                "code": "deadline_vs_wish",
                "text": "Клиент просит раньше, чем расчётный SLA. Дедлайн не подменяли.",
            }
        )

    return texts.model_copy(
        update={"outcome": outcome, "warnings": warnings, "grounds": [f"outcome.{outcome}"]}
    )


def desk_status(outcome: str) -> str:
    return OUTCOME_STATUS.get(outcome, "dispatch")


def _blob(card: dict[str, Any]) -> str:
    parts = [
        card["intake"].get("text") or "",
        slot(card, "problem").get("value") or "",
        slot(card, "symptoms").get("value") or "",
        slot(card, "desired_deadline").get("value") or "",
    ]
    return " ".join(parts).lower()


def _wants_repair(blob: str) -> bool:
    return any(word in blob for word in ("менять", "ремонт", "не запускается"))


def _wants_today(blob: str) -> bool:
    return "сегодня" in blob
