"""Live S1–S4 against a running Reflex + mock. Not part of default pytest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx

BASE = "http://127.0.0.1:8000"
RECEIVED = "2026-08-13T16:40:00+03:00"

SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "S1",
        "intake": {
            "channel": "email",
            "sender": None,
            "received_at": RECEIVED,
            "text": (
                "СеверФуд, склад на Дмитровском шоссе, 100. "
                "ХУ-18 не запускается после перезагрузки. "
                "Продукцию пока перенесли в соседнюю камеру. Нужен выезд специалиста."
            ),
        },
        "expect": {
            "outcome": "create",
            "customer": ("resolved", "C-101"),
            "site": ("resolved", "S-MSK-01"),
            "asset": ("resolved", "A-1003"),
            "history_not": "resolved",
            "tryon": True,
            "auto": True,
        },
    },
    {
        "id": "S2",
        "intake": {
            "channel": "email",
            "sender": "Андрей, СеверФуд",
            "received_at": RECEIVED,
            "text": (
                "Снова 17-я: температура уже +8 и продолжает расти. "
                "Вчера мастер говорил, что если повторится, нужно менять компрессор. "
                "Резервная камера вроде работает. Нужен человек сегодня до 19:00."
            ),
        },
        "expect": {
            "outcome": "clarify",
            "customer": ("resolved", "C-101"),
            "site_not": "resolved",
            "asset": ("ambiguous", None),
            "tryon": False,
            "auto": False,
        },
    },
    {
        "id": "S3",
        "intake": {
            "channel": "call",
            "sender": "Андрей, СеверФуд",
            "received_at": RECEIVED,
            "text": (
                "Это Андрей из СеверФуда, объект на Дмитровском. "
                "Я уже писал минут сорок назад по семнадцатой установке. "
                "Сейчас температура 8,3. Резервная камера есть, "
                "но мы не уверены, что она выдержит весь товар."
            ),
        },
        "expect": {
            "outcome": "update",
            "customer": ("resolved", "C-101"),
            "site": ("resolved", "S-MSK-01"),
            "asset": ("resolved", "A-1001"),
            "history": ("resolved", "T-884"),
            "tryon": True,
            "auto": True,
            "ticket": "T-884",
        },
    },
    {
        "id": "S4",
        "intake": {
            "channel": "email",
            "sender": "Андрей, СеверФуд",
            "received_at": RECEIVED,
            "text": (
                "СеверФуд, склад на Дмитровском шоссе, 100. "
                "КМ-9 не держит температуру, уже +6. Нужен мастер сегодня."
            ),
        },
        "expect": {
            "outcome": "clarify",
            "customer": ("resolved", "C-101"),
            "site": ("resolved", "S-MSK-01"),
            "asset": ("not_found", None),
            "history_not": "resolved",
            "tryon": False,
            "auto": False,
        },
    },
]


def binding(card: dict[str, Any], name: str) -> dict[str, Any]:
    return (card.get("facts") or {}).get(name, {}).get("binding") or {}


def wait_finished(client: httpx.Client, appeal_id: int) -> tuple[dict[str, Any], list[str]]:
    finished: dict[str, Any] = {}
    tools: list[str] = []
    with client.stream("GET", f"/api/v1/appeals/{appeal_id}/stream", timeout=120.0) as stream:
        event = "message"
        data_lines: list[str] = []
        for raw in stream.iter_lines():
            if raw == "":
                if data_lines:
                    payload = json.loads("\n".join(data_lines))
                    if event == "tool_call":
                        name = payload.get("name")
                        if isinstance(name, str) and name:
                            tools.append(name)
                    if event == "run_finished":
                        finished = payload
                        break
                event = "message"
                data_lines = []
                continue
            if raw.startswith("event:"):
                event = raw.split(":", 1)[1].strip()
            elif raw.startswith("data:"):
                data_lines.append(raw.split(":", 1)[1].lstrip())
    return finished, tools


def tools_from_messages(items: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for item in items:
        if item.get("kind") != "tool_call":
            continue
        body = item.get("body") or {}
        name = body.get("name")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def check_tools(names: list[str], outcome: str | None) -> list[str]:
    searches = [index for index, name in enumerate(names) if name.startswith("search_")]
    if not searches:
        return ["no search_* in trace"]
    first = searches[0]
    if not any(name == "update_card" for name in names[first + 1 :]):
        return ["no update_card after first search_*"]
    if outcome in {"create", "update"} and "calculate" not in names:
        return ["no calculate on create/update"]
    return []


def check(card: dict[str, Any], expect: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    decision = card.get("decision") or {}
    if decision.get("outcome") != expect["outcome"]:
        errors.append(f"outcome {decision.get('outcome')} != {expect['outcome']}")
    for slot_name in ("customer", "site", "asset", "history"):
        if slot_name not in expect:
            continue
        status, ident = expect[slot_name]
        got = binding(card, slot_name)
        if got.get("status") != status:
            errors.append(f"{slot_name}.status {got.get('status')} != {status}")
        if ident and got.get("id") != ident:
            errors.append(f"{slot_name}.id {got.get('id')} != {ident}")
    for slot_name in ("site_not", "history_not"):
        if slot_name not in expect:
            continue
        name = slot_name.removesuffix("_not")
        if binding(card, name).get("status") == expect[slot_name]:
            errors.append(f"{name} must not be {expect[slot_name]}")
    dry = decision.get("itsm_dry_run")
    if expect["tryon"] and not dry:
        errors.append("expected ITSM try-on")
    if not expect["tryon"] and dry:
        errors.append("unexpected ITSM try-on")
    if bool(decision.get("auto_in_prod")) != expect["auto"]:
        errors.append(f"auto_in_prod {decision.get('auto_in_prod')} != {expect['auto']}")
    ticket = expect.get("ticket")
    if ticket and (decision.get("ticket_draft") or {}).get("ticket_id") != ticket:
        errors.append(f"ticket {(decision.get('ticket_draft') or {}).get('ticket_id')} != {ticket}")
    return errors


def main() -> int:
    report: list[dict[str, Any]] = []
    failed = 0
    with httpx.Client(base_url=BASE, timeout=30.0) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"login": "dispatcher", "password": "secret"},
        )
        login.raise_for_status()
        for scenario in SCENARIOS:
            created = client.post("/api/v1/appeals", json=scenario["intake"])
            created.raise_for_status()
            appeal_id = int(created.json()["id"])
            _finished, stream_tools = wait_finished(client, appeal_id)
            detail = client.get(f"/api/v1/appeals/{appeal_id}").json()
            messages = client.get(f"/api/v1/appeals/{appeal_id}/messages").json()
            card = detail["card"]
            tool_names = stream_tools or tools_from_messages(messages.get("items") or [])
            errors = check(card, scenario["expect"]) + check_tools(
                tool_names,
                (card.get("decision") or {}).get("outcome"),
            )
            row = {
                "id": scenario["id"],
                "appeal_id": appeal_id,
                "status": detail.get("status"),
                "outcome": (card.get("decision") or {}).get("outcome"),
                "tools": tool_names,
                "errors": errors,
            }
            report.append(row)
            mark = "FAIL" if errors else "OK"
            if errors:
                failed += 1
            print(f"{scenario['id']} appeal={appeal_id} {mark} {errors or row['outcome']}")
    out = Path(__file__).resolve().parents[1] / "docs/sprints/sprint-06-accept-s1-s4/report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
