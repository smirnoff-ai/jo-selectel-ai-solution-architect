from datetime import datetime
from typing import Any

from backend.agent.complete_catalog import asset_query, complete_catalog, customer_query
from backend.agent.run_context import RunContext
from backend.card_template import empty_card


class _FakeMock:
    def get(self, path: str, params: dict[str, Any] | None = None) -> tuple[int, Any]:
        params = params or {}
        if path.endswith("/sites"):
            return 200, {
                "items": [
                    {
                        "site_id": "S-MSK-01",
                        "customer_id": "C-101",
                        "customer_name": "СеверФуд",
                        "address": "Москва, Дмитровское шоссе, 100",
                    },
                    {
                        "site_id": "S-EKB-02",
                        "customer_id": "C-101",
                        "customer_name": "СеверФуд",
                        "address": "Екатеринбург, улица Монтажников, 7",
                    },
                ]
            }
        if path.endswith("/assets"):
            if params.get("site_id") == "S-MSK-01":
                return 200, {
                    "items": [
                        {
                            "asset_id": "A-1001",
                            "site_id": "S-MSK-01",
                            "local_code": "ХУ-17",
                            "address": "Москва, Дмитровское шоссе, 100",
                            "customer_id": "C-101",
                            "customer_name": "СеверФуд",
                        }
                    ]
                }
            return 200, {
                "items": [
                    {
                        "asset_id": "A-1001",
                        "site_id": "S-MSK-01",
                        "local_code": "ХУ-17",
                        "address": "Москва, Дмитровское шоссе, 100",
                        "customer_id": "C-101",
                        "customer_name": "СеверФуд",
                    },
                    {
                        "asset_id": "A-1002",
                        "site_id": "S-EKB-02",
                        "local_code": "ХУ-17",
                        "address": "Екатеринбург, улица Монтажников, 7",
                        "customer_id": "C-101",
                        "customer_name": "СеверФуд",
                    },
                ]
            }
        if path.endswith("/tickets"):
            return 200, {
                "items": [
                    {
                        "ticket_id": "T-884",
                        "customer_id": "C-101",
                        "site_id": "S-MSK-01",
                        "asset_id": "A-1001",
                        "status": "in_progress",
                        "summary": "ХУ-17",
                    }
                ]
            }
        if path.endswith("/contracts"):
            return 200, {
                "items": [
                    {
                        "contract_id": "K-101",
                        "site_id": "S-MSK-01",
                        "plan": "Gold",
                        "response_sla": "60_minutes",
                        "service_window": "24x7",
                        "coverage": ["repair"],
                    }
                ]
            }
        return 404, {"detail": path}


def _card() -> dict:
    return empty_card(
        channel="call",
        sender="Андрей, СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="объект на Дмитровском. уже писал по семнадцатой установке.",
        attachment_text=None,
    )


def test_customer_query_skips_person() -> None:
    card = _card()
    card["facts"]["customer"]["mention"] = "СеверФуд"
    assert customer_query(card) == "СеверФуд"
    card["facts"]["customer"]["mention"] = "Андрей"
    assert customer_query(card) == "СеверФуд"


def test_asset_query_ordinal() -> None:
    assert asset_query("семнадцатая установка") == "17"
    assert asset_query("17-я") == "17"
    assert asset_query("КМ-9").casefold() == "км-9"


def test_complete_catalog_s3_like() -> None:
    card = _card()
    card["facts"]["customer"]["mention"] = "СеверФуд"
    card["facts"]["site"]["mention"] = "объект на Дмитровском"
    card["facts"]["asset"]["mention"] = "семнадцатая установка"
    ctx = RunContext(appeal_id=3, card=card, mock=_FakeMock())  # type: ignore[arg-type]
    complete_catalog(ctx)
    assert card["facts"]["customer"]["binding"]["id"] == "C-101"
    assert card["facts"]["site"]["binding"]["id"] == "S-MSK-01"
    assert card["facts"]["asset"]["binding"]["id"] == "A-1001"
    assert card["facts"]["history"]["binding"]["id"] == "T-884"
    assert card["contract"]["id"] == "K-101"
