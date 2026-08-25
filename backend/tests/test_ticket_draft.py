from datetime import datetime

from backend.agent.ticket_draft import build_ticket_draft, support_clear
from backend.card_template import empty_card


def _card() -> dict:
    return empty_card(
        channel="email",
        sender="СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Склад, установка не запускается",
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
    return card


def test_support_clear_empty_card_is_false() -> None:
    assert support_clear(_card(), "create") is False


def test_support_clear_create_when_bindings_resolved() -> None:
    assert support_clear(_filled(_card()), "create") is True


def test_support_clear_create_false_when_ticket_exists() -> None:
    card = _filled(_card())
    card["facts"]["history"]["binding"] = {
        "status": "resolved",
        "id": "T-1",
        "label": "Заявка",
        "candidates": [],
    }
    assert support_clear(card, "create") is False
    assert support_clear(card, "update") is True


def test_build_ticket_draft_none_without_support() -> None:
    assert build_ticket_draft(_card(), "create") is None
