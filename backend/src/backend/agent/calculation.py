from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from backend.agent.card_slots import binding_status, slot

STEPS = ("low", "medium", "high", "critical")


def recalc(card: dict[str, Any]) -> None:
    site_ok = binding_status(card, "site") == "resolved"
    asset_ok = binding_status(card, "asset") == "resolved"
    history_ok = binding_status(card, "history") == "resolved"
    if not site_ok and not asset_ok:
        card["calculation"] = {
            "branch": "none",
            "status": "blocked",
            "priority": {
                "value": None,
                "formula": None,
                "arguments": {},
                "missing": ["site_or_asset"],
            },
            "sla": {"code": None, "formula": None, "arguments": {}, "missing": ["contract"]},
            "deadline": {
                "at": None,
                "timezone": None,
                "formula": None,
                "arguments": {},
                "missing": ["contract"],
            },
        }
        return

    branch = "update" if history_ok else "create"
    problem = slot(card, "problem").get("value") or ""
    symptoms = f"{slot(card, 'symptoms').get('value') or ''} {problem}"
    intake = card["intake"]["text"]
    blob = f"{symptoms} {intake}".lower()
    criticality = _asset_criticality(card) if asset_ok else None
    priority, formula, arguments = _priority(criticality, blob, card if history_ok else None)

    contract = card.get("contract") or {}
    sla_code = contract.get("response_sla") if contract.get("status") == "resolved" else None
    timezone = _timezone(card)
    received = datetime.fromisoformat(card["intake"]["received_at"])
    deadline_at, sla_formula, deadline_args, missing = _deadline(
        sla_code,
        received,
        timezone,
        contract.get("service_window"),
    )

    card["calculation"] = {
        "branch": branch,
        "status": "computed" if sla_code else "partial",
        "priority": {
            "value": priority,
            "formula": formula,
            "arguments": arguments,
            "missing": [],
        },
        "sla": {
            "code": sla_code,
            "formula": "код договора выбранной площадки" if sla_code else None,
            "arguments": {"contract_id": contract.get("id"), "plan": contract.get("plan")}
            if sla_code
            else {},
            "missing": [] if sla_code else ["contract"],
        },
        "deadline": {
            "at": deadline_at,
            "timezone": timezone,
            "formula": sla_formula,
            "arguments": deadline_args,
            "missing": missing,
        },
    }


def _asset_criticality(card: dict[str, Any]) -> str | None:
    for item in slot(card, "asset").get("evidences") or []:
        record = item.get("record") or {}
        if record.get("id") and item.get("source") == "eam":
            break
    # criticality is not stored on card; caller of search keeps it in result only.
    # We stash last asset criticality on card facts.asset when resolving.
    return card["facts"]["asset"].get("criticality")


def _priority(
    criticality: str | None,
    blob: str,
    card_for_ticket: dict[str, Any] | None,
) -> tuple[str, str, dict[str, Any]]:
    if criticality == "high":
        base = "high"
    elif criticality == "medium" or criticality or "температур" in blob or "не запускается" in blob:
        base = "medium"
    else:
        base = "low"

    bump = "+8" in blob or "+ 8" in blob or "растёт" in blob or "не запускается" in blob
    # also numeric 8,3 / 8.3
    if "8,3" in blob or "8.3" in blob or "+8" in blob:
        bump = True
    value = _step_up(base) if bump else base

    arguments: dict[str, Any] = {"asset_criticality": criticality, "symptoms": blob[:80]}
    if card_for_ticket is not None:
        ticket_priority = card_for_ticket["facts"]["history"].get("ticket_priority")
        if ticket_priority in STEPS:
            value = _max_step(value, ticket_priority)
            arguments["ticket_priority"] = ticket_priority

    return (
        value,
        "критичность актива и симптомы; при обновлении не ниже тикета",
        arguments,
    )


def _deadline(
    sla_code: str | None,
    received: datetime,
    timezone: str | None,
    window: str | None,
) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
    if not sla_code or not timezone:
        return None, None, {}, ["contract" if not sla_code else "timezone"]
    zone = ZoneInfo(timezone)
    local = received.astimezone(zone)
    if sla_code == "60_minutes":
        at = local + timedelta(minutes=60)
        return (
            at.isoformat(),
            "получено + 60 минут, окно 24x7",
            {
                "received_at": received.isoformat(),
                "response_sla": sla_code,
                "service_window": window,
            },
            [],
        )
    if sla_code == "4_business_hours":
        at = _add_business_hours(local, 4)
        return (
            at.isoformat(),
            "4 рабочих часа в окне weekdays_09_18_local",
            {"received_at": received.isoformat(), "response_sla": sla_code},
            [],
        )
    if sla_code == "next_business_day":
        at = _next_business_morning(local)
        return (
            at.isoformat(),
            "09:00 следующего рабочего дня",
            {"received_at": received.isoformat(), "response_sla": sla_code},
            [],
        )
    return None, None, {}, ["unknown_sla"]


def _add_business_hours(start: datetime, hours: int) -> datetime:
    cursor = start
    left = timedelta(hours=hours)
    while left > timedelta(0):
        if cursor.weekday() >= 5:
            cursor = _at_hour(cursor + timedelta(days=1), 9)
            continue
        open_at = _at_hour(cursor, 9)
        close_at = _at_hour(cursor, 18)
        if cursor < open_at:
            cursor = open_at
            continue
        if cursor >= close_at:
            cursor = _at_hour(cursor + timedelta(days=1), 9)
            continue
        piece = min(left, close_at - cursor)
        cursor = cursor + piece
        left -= piece
        if left > timedelta(0):
            cursor = _at_hour(cursor + timedelta(days=1), 9)
    return cursor


def _next_business_morning(local: datetime) -> datetime:
    cursor = local
    if cursor.weekday() < 5 and cursor.hour < 18:
        nxt = cursor + timedelta(days=1)
    else:
        nxt = cursor + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return _at_hour(nxt, 9)


def _at_hour(moment: datetime, hour: int) -> datetime:
    return moment.replace(hour=hour, minute=0, second=0, microsecond=0)


def _timezone(card: dict[str, Any]) -> str | None:
    return card["facts"]["site"].get("timezone") or "Europe/Moscow"


def _step_up(value: str) -> str:
    idx = STEPS.index(value)
    return STEPS[min(idx + 1, len(STEPS) - 1)]


def _max_step(left: str, right: str) -> str:
    return STEPS[max(STEPS.index(left), STEPS.index(right))]


def stash_asset_criticality(card: dict[str, Any], items: list[dict[str, Any]]) -> None:
    if len(items) == 1:
        card["facts"]["asset"]["criticality"] = items[0].get("criticality")
        card["facts"]["site"]["timezone"] = card["facts"]["site"].get("timezone")


def stash_site_timezone(card: dict[str, Any], items: list[dict[str, Any]]) -> None:
    if len(items) == 1:
        card["facts"]["site"]["timezone"] = items[0].get("timezone")


def stash_ticket_priority(card: dict[str, Any], items: list[dict[str, Any]]) -> None:
    open_items = [
        row for row in items if row.get("status") in {"new", "in_progress", "waiting_for_customer"}
    ]
    if len(open_items) == 1:
        card["facts"]["history"]["ticket_priority"] = open_items[0].get("priority")
