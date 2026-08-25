from datetime import datetime

from backend.agent.calculation import compute_calculation


def test_gold_deadline_plus_60() -> None:
    block = compute_calculation(
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        timezone="Europe/Moscow",
        response_sla="60_minutes",
        service_window="24x7",
        asset_criticality="medium",
        symptoms_text="ХУ-18 не запускается",
        open_ticket_priority=None,
    )
    assert block["branch"] == "create"
    assert block["status"] == "computed"
    assert block["sla"]["code"] == "60_minutes"
    assert block["deadline"]["at"].startswith("2026-08-13T17:40:00")
    assert block["priority"]["value"] in {"medium", "high"}
    assert block["priority"]["value"] != "low"


def test_without_contract_is_partial() -> None:
    block = compute_calculation(
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        timezone="Europe/Moscow",
        response_sla=None,
        service_window=None,
        asset_criticality="high",
        symptoms_text="температура +8",
        open_ticket_priority=None,
    )
    assert block["status"] == "partial"
    assert "contract" in block["sla"]["missing"]
    assert block["deadline"]["at"] is None


def test_open_ticket_sets_update_branch() -> None:
    block = compute_calculation(
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        timezone="Europe/Moscow",
        response_sla="60_minutes",
        service_window="24x7",
        asset_criticality="medium",
        symptoms_text="температура 8,3",
        open_ticket_priority="high",
    )
    assert block["branch"] == "update"
    assert block["priority"]["value"] in {"high", "critical"}
