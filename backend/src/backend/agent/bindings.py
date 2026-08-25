from typing import Any

from backend.agent.card_slots import add_system_evidence, mentioned, set_binding, slot


def apply_sites(card: dict[str, Any], items: list[dict[str, Any]]) -> list[str]:
    updated: list[str] = []
    if not items:
        if mentioned(card, "customer"):
            set_binding(card, "customer", status="not_found")
            updated.append("facts.customer")
        if mentioned(card, "site"):
            set_binding(card, "site", status="not_found")
            updated.append("facts.site")
        return updated

    customers = {row["customer_id"] for row in items}
    if len(items) == 1:
        row = items[0]
        _resolve_customer(card, row)
        _resolve_site(card, row)
        return ["facts.customer", "facts.site"]

    if len(customers) == 1:
        _resolve_customer(card, items[0])
        set_binding(
            card,
            "site",
            status="ambiguous",
            candidates=[_site_candidate(row) for row in items],
        )
        return ["facts.customer", "facts.site"]

    set_binding(
        card,
        "customer",
        status="ambiguous",
        candidates=[{"id": row["customer_id"], "label": row.get("customer_name")} for row in items],
    )
    set_binding(
        card,
        "site",
        status="ambiguous",
        candidates=[_site_candidate(row) for row in items],
    )
    return ["facts.customer", "facts.site"]


def apply_assets(card: dict[str, Any], items: list[dict[str, Any]]) -> list[str]:
    updated: list[str] = []
    if not items:
        if mentioned(card, "asset"):
            set_binding(card, "asset", status="not_found")
            updated.append("facts.asset")
        return updated

    sites = {row["site_id"] for row in items}
    site_status = slot(card, "site")["binding"]["status"]

    if len(items) == 1:
        row = items[0]
        _resolve_asset(card, row)
        updated.append("facts.asset")
        if site_status != "resolved":
            set_binding(card, "site", status="resolved", id_=row["site_id"], label=row["site_id"])
            add_system_evidence(
                card, "site", source="eam", record_id=row["site_id"], label=row["site_id"]
            )
            updated.append("facts.site")
        return updated

    set_binding(
        card,
        "asset",
        status="ambiguous",
        candidates=[_asset_candidate(row) for row in items],
    )
    updated.append("facts.asset")
    if len(sites) == 1:
        site_id = next(iter(sites))
        if site_status != "resolved":
            set_binding(card, "site", status="resolved", id_=site_id, label=site_id)
            add_system_evidence(card, "site", source="eam", record_id=site_id, label=site_id)
            updated.append("facts.site")
        return updated

    if site_status != "resolved":
        set_binding(
            card,
            "site",
            status="ambiguous",
            candidates=[{"id": site_id, "label": site_id} for site_id in sorted(sites)],
        )
        updated.append("facts.site")
    return updated


def apply_tickets(card: dict[str, Any], items: list[dict[str, Any]]) -> list[str]:
    open_items = [
        row for row in items if row.get("status") in {"new", "in_progress", "waiting_for_customer"}
    ]
    updated: list[str] = []
    if not open_items:
        if mentioned(card, "history"):
            set_binding(card, "history", status="not_found")
            updated.append("facts.history")
        return updated

    if len(open_items) == 1:
        row = open_items[0]
        set_binding(
            card,
            "history",
            status="resolved",
            id_=row["ticket_id"],
            label=row.get("summary"),
        )
        add_system_evidence(
            card,
            "history",
            source="itsm",
            record_id=row["ticket_id"],
            label=row.get("summary"),
        )
        updated.append("facts.history")
        updated.extend(_fill_from_ticket(card, row))
        return updated

    set_binding(
        card,
        "history",
        status="ambiguous",
        candidates=[{"id": row["ticket_id"], "label": row.get("summary")} for row in open_items],
    )
    return ["facts.history"]


def apply_contract(card: dict[str, Any], items: list[dict[str, Any]]) -> str:
    if not items:
        card["contract"] = {
            "status": "not_found",
            "id": None,
            "site_id": slot(card, "site")["binding"]["id"],
            "plan": None,
            "response_sla": None,
            "service_window": None,
            "coverage": [],
        }
        return "not_found"
    if len(items) > 1:
        return "many"
    row = items[0]
    card["contract"] = {
        "status": "resolved",
        "id": row["contract_id"],
        "site_id": row["site_id"],
        "plan": row.get("plan"),
        "response_sla": row.get("response_sla"),
        "service_window": row.get("service_window"),
        "coverage": list(row.get("coverage") or []),
    }
    return "resolved"


def _resolve_customer(card: dict[str, Any], row: dict[str, Any]) -> None:
    set_binding(
        card,
        "customer",
        status="resolved",
        id_=row["customer_id"],
        label=row.get("customer_name"),
    )
    add_system_evidence(
        card,
        "customer",
        source="crm",
        record_id=row["customer_id"],
        label=row.get("customer_name"),
    )


def _resolve_site(card: dict[str, Any], row: dict[str, Any]) -> None:
    set_binding(
        card,
        "site",
        status="resolved",
        id_=row["site_id"],
        label=row.get("address"),
    )
    add_system_evidence(
        card, "site", source="crm", record_id=row["site_id"], label=row.get("address")
    )


def _resolve_asset(card: dict[str, Any], row: dict[str, Any]) -> None:
    set_binding(
        card,
        "asset",
        status="resolved",
        id_=row["asset_id"],
        label=row.get("local_code"),
    )
    add_system_evidence(
        card, "asset", source="eam", record_id=row["asset_id"], label=row.get("local_code")
    )


def _fill_from_ticket(card: dict[str, Any], row: dict[str, Any]) -> list[str]:
    updated: list[str] = []
    pairs = (
        ("customer", row.get("customer_id"), "itsm"),
        ("site", row.get("site_id"), "itsm"),
        ("asset", row.get("asset_id"), "itsm"),
    )
    for name, ident, source in pairs:
        if not ident:
            continue
        current = slot(card, name)["binding"]["status"]
        if current in {"empty", "mentioned"}:
            set_binding(card, name, status="resolved", id_=ident, label=ident)
            add_system_evidence(card, name, source=source, record_id=ident, label=ident)
            updated.append(f"facts.{name}")
    return updated


def _site_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["site_id"],
        "label": row.get("address"),
        "site_id": row["site_id"],
        "customer_id": row.get("customer_id"),
    }


def _asset_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["asset_id"],
        "label": row.get("local_code"),
        "site_id": row.get("site_id"),
    }
