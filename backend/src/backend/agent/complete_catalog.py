"""Добор справочников кодом: модель могла не вызвать поиск."""

from __future__ import annotations

import re
from typing import Any

from backend.agent.bindings import apply_assets, apply_contract, apply_sites, apply_tickets
from backend.agent.calculation import (
    recalc,
    stash_asset_criticality,
    stash_site_timezone,
    stash_ticket_priority,
)
from backend.agent.card_slots import binding_status, slot
from backend.agent.run_context import RunContext

_ORDINALS = (
    ("восемнадцат", "18"),
    ("семнадцат", "17"),
)


def complete_catalog(ctx: RunContext) -> None:
    ensure_sites(ctx)
    _ensure_assets(ctx)
    _ensure_tickets(ctx)
    _ensure_contract(ctx)


def customer_query(card: dict[str, Any]) -> str | None:
    mention = (slot(card, "customer").get("mention") or "").strip()
    sender = str((card.get("intake") or {}).get("sender") or "").strip()
    person = sender.split(",", maxsplit=1)[0].strip() if sender else ""
    org = sender.split(",", maxsplit=1)[1].strip() if "," in sender else ""
    if mention and mention.casefold() != person.casefold():
        return mention
    if org:
        return org
    return mention or None


def asset_query(mention: str) -> str:
    folded = mention.casefold()
    for stem, num in _ORDINALS:
        if stem in folded:
            return num
    ordinal = re.search(r"(\d{1,3})\s*-?\s*я\b", folded)
    if ordinal:
        return ordinal.group(1)
    code = re.search(r"[а-яёa-z]{2,3}-?\s*\d+", folded)
    if code:
        return re.sub(r"\s+", "", code.group(0))
    return mention.strip()


def _catalog_items(
    ctx: RunContext,
    catalog: str,
    path: str,
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    try:
        status, body = ctx.mock.get(path, params)
    except OSError:
        ctx.note_error(catalog)
        return []
    if status >= 400:
        ctx.note_error(catalog)
        return []
    if not isinstance(body, dict):
        return []
    return list(body.get("items") or [])


def ensure_sites(ctx: RunContext) -> None:
    if (
        binding_status(ctx.card, "customer") == "resolved"
        and binding_status(ctx.card, "site") == "resolved"
    ):
        return
    query = customer_query(ctx.card)
    if not query:
        return
    items = _catalog_items(ctx, "crm", "/crm/v1/sites", {"customer_name": query})
    if not items:
        items = _catalog_items(ctx, "crm", "/crm/v1/sites", {"q": query})
    if not items:
        return
    stash_site_timezone(ctx.card, items)
    apply_sites(ctx.card, items, query=query)
    recalc(ctx.card)
    ctx.snapshot()


def _ensure_assets(ctx: RunContext) -> None:
    status = binding_status(ctx.card, "asset")
    mention = (slot(ctx.card, "asset").get("mention") or "").strip()
    if status == "resolved" or not mention:
        return
    if status == "ambiguous" and binding_status(ctx.card, "site") != "resolved":
        return
    params: dict[str, Any] = {"q": asset_query(mention)}
    if binding_status(ctx.card, "site") == "resolved":
        params["site_id"] = slot(ctx.card, "site")["binding"]["id"]
    items = _catalog_items(ctx, "eam", "/eam/v1/assets", params)
    stash_asset_criticality(ctx.card, items)
    apply_assets(ctx.card, items)
    recalc(ctx.card)
    ctx.snapshot()


def _ensure_tickets(ctx: RunContext) -> None:
    if binding_status(ctx.card, "history") == "resolved":
        return
    if binding_status(ctx.card, "asset") != "resolved":
        return
    ident = slot(ctx.card, "asset")["binding"]["id"]
    items = _catalog_items(
        ctx,
        "itsm",
        "/itsm/v1/tickets",
        {"asset_id": ident, "status": "open"},
    )
    stash_ticket_priority(ctx.card, items)
    apply_tickets(ctx.card, items)
    recalc(ctx.card)
    ctx.snapshot()


def _ensure_contract(ctx: RunContext) -> None:
    if (ctx.card.get("contract") or {}).get("status") == "resolved":
        return
    if binding_status(ctx.card, "site") != "resolved":
        return
    ident = slot(ctx.card, "site")["binding"]["id"]
    items = _catalog_items(ctx, "contracts", "/contracts/v1/contracts", {"site_id": ident})
    apply_contract(ctx.card, items)
    recalc(ctx.card)
    ctx.snapshot()
