from datetime import datetime

from backend.agent.finale import Finale
from backend.agent.guard import apply_guard, support_clear
from backend.card_template import empty_card


def _card() -> dict:
    return empty_card(
        channel="email",
        sender="Андрей, СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Снова 17-я",
        attachment_text=None,
    )


def test_create_without_support_becomes_clarify() -> None:
    finale = Finale(outcome="create", reason="заведём")
    decided = apply_guard(_card(), finale, {})
    assert decided.outcome == "clarify"
    assert support_clear(_card(), "create") is False


def test_two_catalog_errors_dispatch() -> None:
    decided = apply_guard(_card(), Finale(outcome="create", reason="x"), {"eam": 2})
    assert decided.outcome == "dispatch"


def test_resolved_without_ticket_is_create() -> None:
    card = _card()
    card["facts"]["customer"]["binding"] = {
        "status": "resolved",
        "id": "C-101",
        "label": "СеверФуд",
        "candidates": [],
    }
    card["facts"]["site"]["binding"] = {
        "status": "resolved",
        "id": "S-MSK-01",
        "label": "Дмитровское",
        "candidates": [],
    }
    card["facts"]["asset"]["binding"] = {
        "status": "resolved",
        "id": "A-1003",
        "label": "ХУ-18",
        "candidates": [],
    }
    card["contract"] = {
        "status": "resolved",
        "id": "K-101",
        "coverage": ["diagnostics", "repair"],
    }
    decided = apply_guard(card, Finale(outcome="clarify", reason="не уверен"), {})
    assert decided.outcome == "create"
    assert support_clear(card, "create") is True
