from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from mock_severholod.seed_store import SeedStore

PRIORITIES = {"low", "medium", "high", "critical"}
OPEN_STATUSES = {"new", "in_progress", "waiting_for_customer"}


def _check(check_id: str, *, passed: bool, detail: str | None = None) -> dict[str, object]:
    row: dict[str, object] = {"id": check_id, "passed": passed}
    if detail is not None:
        row["detail"] = detail
    return row


def _payload_key(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _create_checks(store: SeedStore, body: dict[str, Any]) -> list[dict[str, object]]:
    site = store.get_site(body["site_id"])
    customer_exists = any(row["customer_id"] == body["customer_id"] for row in store.sites)
    contract = store.get_contract(body["contract_id"])
    asset_id = body.get("asset_id")
    asset = store.get_asset(asset_id) if asset_id else None
    summary = (body.get("summary") or "").strip()
    priority = body.get("priority")

    asset_ok = True
    asset_detail = None
    if asset_id:
        asset_ok = asset is not None and asset["site_id"] == body["site_id"]
        if asset is None:
            asset_detail = f"{asset_id} not found"
        elif asset["site_id"] != body["site_id"]:
            asset_detail = f"{asset_id} is not on {body['site_id']}"

    return [
        _check("customer_exists", passed=customer_exists),
        _check("site_exists", passed=site is not None),
        _check(
            "site_belongs_to_customer",
            passed=site is not None and site["customer_id"] == body["customer_id"],
        ),
        _check("asset_belongs_to_site", passed=asset_ok, detail=asset_detail),
        _check("contract_exists", passed=contract is not None),
        _check(
            "contract_belongs_to_site",
            passed=contract is not None and contract["site_id"] == body["site_id"],
        ),
        _check("summary_present", passed=bool(summary)),
        _check("priority_known", passed=priority in PRIORITIES),
    ]


def create_ticket(
    store: SeedStore,
    body: dict[str, Any],
    *,
    persist: bool,
) -> tuple[bool, dict[str, object]]:
    checks = _create_checks(store, body)
    payload = {key: value for key, value in body.items() if value is not None}
    ok = all(bool(row["passed"]) for row in checks)
    if not ok:
        return False, {
            "persisted": False,
            "accepted": False,
            "would_ticket_id": None,
            "would_status": None,
            "payload": payload,
            "checks": checks,
        }

    ticket_id = store.next_ticket_id(_payload_key(payload))
    now = datetime.now(UTC).isoformat()
    if persist:
        store.add_ticket(
            {
                "ticket_id": ticket_id,
                "customer_id": body["customer_id"],
                "site_id": body["site_id"],
                "asset_id": body.get("asset_id"),
                "contract_id": body["contract_id"],
                "status": "new",
                "priority": body["priority"],
                "summary": body["summary"].strip(),
                "created_at": now,
                "updated_at": now,
            }
        )
    return True, {
        "persisted": persist,
        "accepted": True,
        "would_ticket_id": ticket_id,
        "would_status": "new",
        "payload": payload,
        "checks": checks,
    }


def _pick(
    body: dict[str, Any],
    ticket: dict[str, Any] | None,
    field: str,
    default: object = "",
) -> object:
    if body.get(field) is not None:
        return body[field]
    if ticket is not None:
        return ticket.get(field, default)
    return default


def patch_ticket(
    store: SeedStore,
    ticket_id: str,
    body: dict[str, Any],
    *,
    persist: bool,
) -> tuple[bool, dict[str, object]]:
    ticket = store.get_ticket(ticket_id)
    identity_fields = ("customer_id", "site_id", "asset_id", "contract_id")
    identity_mismatch = False
    if ticket is not None:
        identity_mismatch = any(
            body.get(field) is not None and body[field] != ticket[field]
            for field in identity_fields
        )

    merged = {
        "customer_id": _pick(body, ticket, "customer_id"),
        "site_id": _pick(body, ticket, "site_id"),
        "asset_id": _pick(body, ticket, "asset_id", None),
        "contract_id": _pick(body, ticket, "contract_id"),
        "summary": _pick(body, ticket, "summary"),
        "priority": _pick(body, ticket, "priority", None),
    }
    extra = _create_checks(store, merged) if ticket is not None else []
    checks = [
        _check(
            "ticket_exists",
            passed=ticket is not None,
            detail=None if ticket else f"{ticket_id} not found",
        ),
        _check(
            "ticket_is_open",
            passed=ticket is not None and ticket["status"] in OPEN_STATUSES,
        ),
        _check("identity_not_changed", passed=not identity_mismatch),
        *extra,
    ]
    payload = {key: value for key, value in body.items() if value is not None}
    ok = all(bool(row["passed"]) for row in checks)
    if not ok or ticket is None:
        return False, {
            "persisted": False,
            "accepted": False,
            "would_ticket_id": None,
            "would_status": None,
            "payload": payload,
            "checks": checks,
        }

    summary = merged["summary"]
    next_summary = summary.strip() if isinstance(summary, str) else ticket["summary"]
    next_status = body.get("status") or ticket["status"]
    updated = {
        **ticket,
        "summary": next_summary,
        "priority": merged["priority"],
        "status": next_status,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    if persist:
        store.replace_ticket(ticket_id, updated)
    return True, {
        "persisted": persist,
        "accepted": True,
        "would_ticket_id": ticket_id,
        "would_status": next_status,
        "payload": payload,
        "checks": checks,
    }
