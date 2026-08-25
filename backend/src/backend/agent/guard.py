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

_NO_FINALE = "Модель не вернула финал"
_SUPPORT = {"create", "update", "approve", "refuse_auto"}


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
    if any(count >= 2 for count in catalog_errors.values()):
        base = finale or Finale(outcome="dispatch", reason=_NO_FINALE)
        return base.model_copy(update={"outcome": "dispatch", "grounds": ["catalog_errors"]})
    if finale is None:
        return Finale(outcome="dispatch", reason=_NO_FINALE)
    return _with_sla_warning(card, _fix_contradiction(card, finale) or finale)


def desk_status(outcome: str) -> str:
    return OUTCOME_STATUS.get(outcome, "dispatch")


def _fix_contradiction(card: dict[str, Any], finale: Finale) -> Finale | None:
    history = binding_status(card, "history")
    needs_support = finale.outcome in _SUPPORT
    support_fix = _support_slots(card, finale) if needs_support else None
    if support_fix is not None:
        return support_fix
    if finale.outcome == "create" and history == "resolved":
        return finale.model_copy(update={"outcome": "update", "grounds": ["outcome.update"]})
    if finale.outcome == "update" and history != "resolved":
        if support_clear(card, "create"):
            return finale.model_copy(update={"outcome": "create", "grounds": ["outcome.create"]})
        return finale.model_copy(update={"outcome": "clarify", "grounds": ["facts.history"]})
    if needs_support:
        return _contract_override(card, finale)
    return None


def _support_slots(card: dict[str, Any], finale: Finale) -> Finale | None:
    customer_ok = binding_status(card, "customer") == "resolved"
    site_ok = binding_status(card, "site") == "resolved"
    if not customer_ok or not site_ok:
        return finale.model_copy(
            update={"outcome": "clarify", "grounds": ["facts.customer", "facts.site"]}
        )
    if binding_status(card, "asset") in {"ambiguous", "not_found"}:
        return finale.model_copy(update={"outcome": "clarify", "grounds": ["facts.asset.binding"]})
    return None


def _contract_override(card: dict[str, Any], finale: Finale) -> Finale | None:
    coverage = list((card.get("contract") or {}).get("coverage") or [])
    if (card.get("contract") or {}).get("status") == "not_found":
        return finale.model_copy(
            update={"outcome": "refuse_auto", "grounds": ["contract.not_found"]}
        )
    if _wants_repair(_blob(card)) and coverage and "repair" not in coverage:
        return finale.model_copy(update={"outcome": "approve", "grounds": ["coverage"]})
    return None


def _with_sla_warning(card: dict[str, Any], finale: Finale) -> Finale:
    warnings = list(finale.warnings)
    sla = (card.get("calculation") or {}).get("sla", {}).get("code")
    if _wants_today(_blob(card)) and sla in {"next_business_day", "4_business_hours"}:
        warnings.append(
            {
                "code": "deadline_vs_wish",
                "text": "Клиент просит раньше, чем расчётный SLA. Дедлайн не подменяли.",
            }
        )
    if warnings == list(finale.warnings):
        return finale
    return finale.model_copy(update={"warnings": warnings})


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
