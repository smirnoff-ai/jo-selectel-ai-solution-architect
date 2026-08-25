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


def _filled(card: dict) -> dict:
    card["facts"]["customer"]["binding"] = {
        "status": "resolved",
        "id": "C-101",
        "label": "Клиент",
        "candidates": [],
    }
    card["facts"]["site"]["binding"] = {
        "status": "resolved",
        "id": "S-1",
        "label": "Площадка",
        "candidates": [],
    }
    card["facts"]["asset"]["binding"] = {
        "status": "resolved",
        "id": "A-1",
        "label": "Установка",
        "candidates": [],
    }
    card["contract"] = {
        "status": "resolved",
        "id": "K-1",
        "coverage": ["diagnostics", "repair"],
    }
    return card


def test_create_without_support_becomes_clarify() -> None:
    finale = Finale(outcome="create", reason="заведём")
    decided = apply_guard(_card(), finale, {})
    assert decided.outcome == "clarify"
    assert support_clear(_card(), "create") is False


def test_two_catalog_errors_dispatch() -> None:
    decided = apply_guard(_card(), Finale(outcome="create", reason="x"), {"eam": 2})
    assert decided.outcome == "dispatch"


def test_agreed_clarify_stays() -> None:
    card = _filled(_card())
    decided = apply_guard(card, Finale(outcome="clarify", reason="не уверен"), {})
    assert decided.outcome == "clarify"
    assert support_clear(card, "create") is True


def test_agreed_create_stays() -> None:
    card = _filled(_card())
    decided = apply_guard(card, Finale(outcome="create", reason="заведём"), {})
    assert decided.outcome == "create"


def test_missing_finale_is_dispatch() -> None:
    decided = apply_guard(_filled(_card()), None, {})
    assert decided.outcome == "dispatch"
    assert decided.reason == "Модель не вернула финал"


def test_create_when_ticket_exists_becomes_update() -> None:
    card = _filled(_card())
    card["facts"]["history"]["binding"] = {
        "status": "resolved",
        "id": "T-1",
        "label": "Заявка",
        "candidates": [],
    }
    decided = apply_guard(card, Finale(outcome="create", reason="заведём"), {})
    assert decided.outcome == "update"
