from datetime import datetime

import pytest

from backend.agent.patch_merge import MergeRejectedError, merge_update
from backend.agent.schemas.update_card import UpdateCardInput
from backend.card_template import empty_card


def _card() -> dict:
    return empty_card(
        channel="email",
        sender=None,
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Склад, установка не запускается",
        attachment_text=None,
    )


def test_accepts_json_string_identity_slot() -> None:
    patch = UpdateCardInput.model_validate(
        {
            "customer": (
                '{"evidences":[{"kind":"system","source":"crm",'
                '"record":{"system":"crm","id":"C-101","label":"Клиент"},'
                '"confidence":"high"}]}'
            )
        }
    )
    assert patch.customer is not None
    assert patch.customer.evidences[0].record is not None
    assert patch.customer.evidences[0].record.id == "C-101"


def test_accepts_plain_symptoms_string() -> None:
    patch = UpdateCardInput.model_validate({"symptoms": "температура +8"})
    assert patch.symptoms is not None
    assert patch.symptoms.value == "температура +8"


def test_writes_resolved_when_id_seen() -> None:
    card = _card()
    patch = UpdateCardInput.model_validate(
        {
            "site": {
                "mention": "Дмитровское",
                "binding": {
                    "status": "resolved",
                    "id": "S-MSK-01",
                    "label": "Москва, Дмитровское шоссе, 100",
                },
            }
        }
    )
    updated = merge_update(card, patch, seen_ids={"S-MSK-01"}, last_calculation=None)
    assert updated == ["facts.site"]
    assert card["facts"]["site"]["binding"]["id"] == "S-MSK-01"
    assert card["facts"]["site"]["binding"]["status"] == "resolved"


def test_rejects_unknown_id() -> None:
    card = _card()
    patch = UpdateCardInput.model_validate(
        {"asset": {"binding": {"status": "resolved", "id": "A-9999", "label": "нет"}}}
    )
    with pytest.raises(MergeRejectedError, match="A-9999"):
        merge_update(card, patch, seen_ids={"A-1001"}, last_calculation=None)


def test_calculation_writes_last_result_not_invented() -> None:
    card = _card()
    last = {
        "branch": "create",
        "status": "computed",
        "priority": {"value": "high", "formula": "тест", "arguments": {}, "missing": []},
        "sla": {"code": "60_minutes", "formula": None, "arguments": {}, "missing": []},
        "deadline": {"at": "2026-08-13T17:40:00+03:00", "timezone": "Europe/Moscow"},
    }
    patch = UpdateCardInput.model_validate(
        {"calculation": {"priority": {"value": "critical"}, "invented": True}}
    )
    merge_update(card, patch, seen_ids=set(), last_calculation=last)
    assert card["calculation"]["priority"]["value"] == "high"
    assert "invented" not in card["calculation"]


def test_calculation_requires_prior_calculate() -> None:
    card = _card()
    patch = UpdateCardInput.model_validate({"calculation": {"priority": {"value": "high"}}})
    with pytest.raises(MergeRejectedError, match="calculate"):
        merge_update(card, patch, seen_ids=set(), last_calculation=None)


def test_explicit_empty_binding_with_mention_becomes_mentioned() -> None:
    card = _card()
    patch = UpdateCardInput.model_validate(
        {"asset": {"mention": "семнадцатая", "binding": {"status": "empty"}}}
    )
    merge_update(card, patch, seen_ids=set(), last_calculation=None)
    assert card["facts"]["asset"]["binding"]["status"] == "mentioned"


def test_mention_without_binding_becomes_mentioned() -> None:
    card = _card()
    patch = UpdateCardInput.model_validate({"customer": {"mention": "СеверФуд"}})
    merge_update(card, patch, seen_ids=set(), last_calculation=None)
    assert card["facts"]["customer"]["binding"]["status"] == "mentioned"
    assert card["facts"]["customer"]["mention"] == "СеверФуд"
