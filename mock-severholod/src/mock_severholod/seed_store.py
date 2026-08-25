from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def _contains(value: str, query: str) -> bool:
    return query.casefold() in value.casefold()


class SeedStore:
    def __init__(self, seed_path: Path) -> None:
        raw = json.loads(seed_path.read_text(encoding="utf-8"))
        self.sites: list[dict[str, Any]] = raw["sites"]
        self.assets: list[dict[str, Any]] = raw["assets"]
        self.contracts: list[dict[str, Any]] = raw["contracts"]
        self.tickets: list[dict[str, Any]] = deepcopy(raw["tickets"])
        self.dry_run_ids: dict[str, str] = {}

    def get_site(self, site_id: str) -> dict[str, Any] | None:
        return next((row for row in self.sites if row["site_id"] == site_id), None)

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        return next((row for row in self.assets if row["asset_id"] == asset_id), None)

    def get_contract(self, contract_id: str) -> dict[str, Any] | None:
        return next((row for row in self.contracts if row["contract_id"] == contract_id), None)

    def get_ticket(self, ticket_id: str) -> dict[str, Any] | None:
        return next((row for row in self.tickets if row["ticket_id"] == ticket_id), None)

    def search_sites(
        self,
        *,
        q: str | None,
        customer_id: str | None,
        site_id: str | None,
        customer_name: str | None,
        address: str | None,
        timezone: str | None,
    ) -> list[dict[str, Any]]:
        rows = list(self.sites)
        if customer_id:
            rows = [row for row in rows if row["customer_id"] == customer_id]
        if site_id:
            rows = [row for row in rows if row["site_id"] == site_id]
        if customer_name:
            rows = [row for row in rows if _contains(row["customer_name"], customer_name)]
        if address:
            rows = [row for row in rows if _contains(row["address"], address)]
        if timezone:
            rows = [row for row in rows if row["timezone"] == timezone]
        if q:
            rows = [
                row
                for row in rows
                if _contains(row["customer_name"], q)
                or _contains(row["address"], q)
                or _contains(row["site_id"], q)
                or _contains(row["customer_id"], q)
            ]
        return rows

    def search_assets(
        self,
        *,
        q: str | None,
        asset_id: str | None,
        site_id: str | None,
        local_code: str | None,
        asset_type: str | None,
        criticality: str | None,
    ) -> list[dict[str, Any]]:
        rows = list(self.assets)
        if asset_id:
            rows = [row for row in rows if row["asset_id"] == asset_id]
        if site_id:
            rows = [row for row in rows if row["site_id"] == site_id]
        if local_code:
            rows = [row for row in rows if _contains(row["local_code"], local_code)]
        if asset_type:
            rows = [row for row in rows if _contains(row["asset_type"], asset_type)]
        if criticality:
            rows = [row for row in rows if row["criticality"] == criticality]
        if q:
            rows = [
                row
                for row in rows
                if _contains(row["local_code"], q)
                or _contains(row["asset_id"], q)
                or _contains(row["asset_type"], q)
            ]
        enriched: list[dict[str, Any]] = []
        for row in rows:
            site = self.get_site(row["site_id"]) or {}
            enriched.append(
                {
                    **row,
                    "address": site.get("address"),
                    "customer_id": site.get("customer_id"),
                    "customer_name": site.get("customer_name"),
                }
            )
        return enriched

    def search_contracts(self, site_id: str) -> list[dict[str, Any]]:
        return [row for row in self.contracts if row["site_id"] == site_id]

    def search_tickets(
        self,
        *,
        customer_id: str | None,
        site_id: str | None,
        asset_id: str | None,
        contract_id: str | None,
        status: str | None,
    ) -> list[dict[str, Any]]:
        open_statuses = {"new", "in_progress", "waiting_for_customer"}
        rows = list(self.tickets)
        if customer_id:
            rows = [row for row in rows if row["customer_id"] == customer_id]
        if site_id:
            rows = [row for row in rows if row["site_id"] == site_id]
        if asset_id:
            rows = [row for row in rows if row["asset_id"] == asset_id]
        if contract_id:
            rows = [row for row in rows if row["contract_id"] == contract_id]
        if status == "open":
            rows = [row for row in rows if row["status"] in open_statuses]
        elif status:
            rows = [row for row in rows if row["status"] == status]
        return rows

    def next_ticket_id(self, payload_key: str) -> str:
        cached = self.dry_run_ids.get(payload_key)
        if cached:
            return cached
        numbers = [int(row["ticket_id"].split("-", maxsplit=1)[1]) for row in self.tickets]
        numbers.extend(int(tid.split("-", maxsplit=1)[1]) for tid in self.dry_run_ids.values())
        nxt = f"T-{max(numbers, default=0) + 1}"
        self.dry_run_ids[payload_key] = nxt
        return nxt

    def add_ticket(self, ticket: dict[str, Any]) -> None:
        self.tickets.append(ticket)

    def replace_ticket(self, ticket_id: str, ticket: dict[str, Any]) -> None:
        self.tickets = [ticket if row["ticket_id"] == ticket_id else row for row in self.tickets]
