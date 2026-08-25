from datetime import datetime
from pathlib import Path

from backend.agent import factory
from backend.agent.runner import apply_card_decision
from backend.card_template import empty_card


class _FakeMock:
    def __init__(self) -> None:
        self.posts: list[tuple[str, dict]] = []

    def post(self, path: str, payload: dict) -> tuple[int, dict]:
        self.posts.append((path, payload))
        return 200, {"accepted": True, "would_ticket_id": "T-9001"}

    def patch(self, _path: str, _payload: dict) -> tuple[int, dict]:
        return 200, {"accepted": True, "ticket_id": "T-884"}


def _card() -> dict:
    return empty_card(
        channel="email",
        sender="СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Склад, установка не запускается",
        attachment_text=None,
    )


def test_apply_card_decision_keeps_model_outcome() -> None:
    card = _card()
    card["decision"] = {
        "outcome": "create",
        "reason": "модель так решила",
        "grounds": ["однозначная площадка"],
    }
    outcome = apply_card_decision(card, _FakeMock())
    assert outcome == "create"
    assert card["decision"]["outcome"] == "create"
    assert card["decision"]["reason"] == "модель так решила"
    assert card["decision"]["grounds"] == ["однозначная площадка"]
    assert card["decision"]["auto_in_prod"] is False


def test_apply_card_decision_clarify_clears_tryon() -> None:
    card = _card()
    card["decision"] = {
        "outcome": "clarify",
        "reason": "две площадки",
        "ticket_draft": {"summary": "x"},
        "itsm_dry_run": {"accepted": True},
        "auto_in_prod": True,
    }
    outcome = apply_card_decision(card, _FakeMock())
    assert outcome == "clarify"
    assert card["decision"]["ticket_draft"] is None
    assert card["decision"]["itsm_dry_run"] is None
    assert card["decision"]["auto_in_prod"] is False


def test_apply_card_decision_empty_is_dispatch() -> None:
    card = _card()
    mock = _FakeMock()
    outcome = apply_card_decision(card, mock)
    assert outcome == "dispatch"
    assert mock.posts == []
    assert card["decision"]["auto_in_prod"] is False


def test_factory_has_no_finale_strategy() -> None:
    text = Path(factory.__file__).read_text(encoding="utf-8")
    assert "ToolStrategy" not in text
    assert "Finale" not in text
    assert "response_format" not in text
