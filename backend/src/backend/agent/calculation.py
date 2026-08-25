from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

STEPS = ("low", "medium", "high", "critical")


def compute_calculation(
    *,
    received_at: datetime,
    timezone: str | None,
    response_sla: str | None,
    service_window: str | None,
    asset_criticality: str | None,
    symptoms_text: str,
    open_ticket_priority: str | None,
) -> dict[str, Any]:
    blob = symptoms_text.lower()
    priority, formula, arguments = _priority(asset_criticality, blob, open_ticket_priority)
    deadline_at, sla_formula, deadline_args, missing = _deadline(
        response_sla,
        received_at,
        timezone,
        service_window,
    )
    sla_ok = bool(response_sla) and not missing
    return {
        "branch": "update" if open_ticket_priority else "create",
        "status": "computed" if sla_ok else "partial",
        "priority": {
            "value": priority,
            "formula": formula,
            "arguments": arguments,
            "missing": [],
        },
        "sla": {
            "code": response_sla,
            "formula": "код договора выбранной площадки" if response_sla else None,
            "arguments": {"response_sla": response_sla} if response_sla else {},
            "missing": [] if response_sla else ["contract"],
        },
        "deadline": {
            "at": deadline_at,
            "timezone": timezone,
            "formula": sla_formula,
            "arguments": deadline_args,
            "missing": missing,
        },
    }


def _priority(
    criticality: str | None,
    blob: str,
    ticket_priority: str | None,
) -> tuple[str, str, dict[str, Any]]:
    if criticality == "high":
        base = "high"
    elif criticality == "medium" or criticality or "температур" in blob or "не запускается" in blob:
        base = "medium"
    else:
        base = "low"

    bump = "+8" in blob or "+ 8" in blob or "растёт" in blob or "не запускается" in blob
    if "8,3" in blob or "8.3" in blob or "+8" in blob:
        bump = True
    value = _step_up(base) if bump else base

    arguments: dict[str, Any] = {"asset_criticality": criticality, "symptoms": blob[:80]}
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
    nxt = local + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return _at_hour(nxt, 9)


def _at_hour(moment: datetime, hour: int) -> datetime:
    return moment.replace(hour=hour, minute=0, second=0, microsecond=0)


def _step_up(value: str) -> str:
    idx = STEPS.index(value)
    return STEPS[min(idx + 1, len(STEPS) - 1)]


def _max_step(left: str, right: str) -> str:
    return STEPS[max(STEPS.index(left), STEPS.index(right))]
