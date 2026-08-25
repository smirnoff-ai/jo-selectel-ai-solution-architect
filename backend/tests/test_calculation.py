from datetime import datetime

from backend.agent.calculation import recalc
from backend.card_template import empty_card


def test_gold_deadline_plus_60() -> None:
    card = empty_card(
        channel="email",
        sender=None,
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="ХУ-18 не запускается",
        attachment_text=None,
    )
    card["facts"]["site"]["binding"] = {
        "status": "resolved",
        "id": "S-MSK-01",
        "label": "Дмитровское",
        "candidates": [],
    }
    card["facts"]["site"]["timezone"] = "Europe/Moscow"
    card["facts"]["asset"]["binding"] = {
        "status": "resolved",
        "id": "A-1003",
        "label": "ХУ-18",
        "candidates": [],
    }
    card["facts"]["asset"]["criticality"] = "medium"
    card["facts"]["problem"]["value"] = "не запускается"
    card["contract"] = {
        "status": "resolved",
        "id": "K-101",
        "site_id": "S-MSK-01",
        "plan": "Gold",
        "response_sla": "60_minutes",
        "service_window": "24x7",
        "coverage": ["repair"],
    }
    recalc(card)
    assert card["calculation"]["branch"] == "create"
    assert card["calculation"]["sla"]["code"] == "60_minutes"
    assert card["calculation"]["deadline"]["at"].startswith("2026-08-13T17:40:00")
    assert card["calculation"]["priority"]["value"] in {"medium", "high"}
    assert card["calculation"]["priority"]["value"] != "low"
