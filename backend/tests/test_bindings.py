from datetime import datetime

from backend.agent.bindings import apply_assets, apply_contract, apply_sites, apply_tickets
from backend.card_template import empty_card


def _card() -> dict:
    return empty_card(
        channel="email",
        sender="Андрей, СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Снова 17-я",
        attachment_text=None,
    )


def test_dmitrov_text_narrows_two_sites() -> None:
    card = _card()
    card["intake"]["text"] = "объект на Дмитровском, семнадцатая установка"
    apply_sites(
        card,
        [
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
        ],
    )
    assert card["facts"]["site"]["binding"]["id"] == "S-MSK-01"


def test_empty_after_resolve_keeps_customer() -> None:
    card = _card()
    card["facts"]["customer"]["mention"] = "Андрей"
    apply_sites(
        card,
        [
            {
                "site_id": "S-MSK-01",
                "customer_id": "C-101",
                "customer_name": "СеверФуд",
                "address": "Дмитровское",
            }
        ],
    )
    apply_sites(card, [], query="Андрей")
    assert card["facts"]["customer"]["binding"]["id"] == "C-101"


def test_ticket_ignored_when_asset_missing() -> None:
    card = _card()
    card["facts"]["asset"]["mention"] = "КМ-9"
    card["facts"]["asset"]["binding"]["status"] = "not_found"
    apply_tickets(
        card,
        [
            {
                "ticket_id": "T-884",
                "customer_id": "C-101",
                "site_id": "S-MSK-01",
                "asset_id": "A-1001",
                "status": "in_progress",
                "summary": "ХУ-17",
            }
        ],
    )
    assert card["facts"]["history"]["binding"]["status"] == "empty"


def test_two_sites_same_customer_site_ambiguous() -> None:
    card = _card()
    card["facts"]["customer"]["mention"] = "СеверФуд"
    apply_sites(
        card,
        [
            {
                "site_id": "S-MSK-01",
                "customer_id": "C-101",
                "customer_name": "СеверФуд",
                "address": "Дмитровское",
            },
            {
                "site_id": "S-EKB-02",
                "customer_id": "C-101",
                "customer_name": "СеверФуд",
                "address": "Монтажников",
            },
        ],
    )
    assert card["facts"]["customer"]["binding"]["status"] == "resolved"
    assert card["facts"]["customer"]["binding"]["id"] == "C-101"
    assert card["facts"]["site"]["binding"]["status"] == "ambiguous"
    assert len(card["facts"]["site"]["binding"]["candidates"]) == 2


def test_dmitrov_text_narrows_two_assets() -> None:
    card = _card()
    card["intake"]["text"] = "объект на Дмитровском, семнадцатая установка"
    apply_assets(
        card,
        [
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
        ],
    )
    assert card["facts"]["asset"]["binding"]["id"] == "A-1001"
    assert card["facts"]["site"]["binding"]["id"] == "S-MSK-01"
    assert card["facts"]["customer"]["binding"]["id"] == "C-101"


def test_ticket_ignored_when_asset_ambiguous() -> None:
    card = _card()
    card["facts"]["asset"]["binding"]["status"] = "ambiguous"
    apply_tickets(
        card,
        [
            {
                "ticket_id": "T-884",
                "customer_id": "C-101",
                "site_id": "S-MSK-01",
                "asset_id": "A-1001",
                "status": "in_progress",
                "summary": "ХУ-17",
            }
        ],
    )
    assert card["facts"]["history"]["binding"]["status"] == "empty"


def test_two_hu17_asset_ambiguous() -> None:
    card = _card()
    card["facts"]["asset"]["mention"] = "17-я"
    apply_assets(
        card,
        [
            {"asset_id": "A-1001", "site_id": "S-MSK-01", "local_code": "ХУ-17"},
            {"asset_id": "A-1002", "site_id": "S-EKB-02", "local_code": "ХУ-17"},
        ],
    )
    assert card["facts"]["asset"]["binding"]["status"] == "ambiguous"
    assert card["facts"]["site"]["binding"]["status"] == "ambiguous"


def test_one_asset_resolves_site() -> None:
    card = _card()
    apply_assets(
        card,
        [{"asset_id": "A-1003", "site_id": "S-MSK-01", "local_code": "ХУ-18"}],
    )
    assert card["facts"]["asset"]["binding"]["id"] == "A-1003"
    assert card["facts"]["site"]["binding"]["id"] == "S-MSK-01"


def test_empty_person_query_does_not_bury_customer() -> None:
    card = _card()
    card["facts"]["customer"]["mention"] = "СеверФуд"
    apply_sites(card, [], query="Андрей")
    assert card["facts"]["customer"]["binding"]["status"] == "empty"


def test_filtered_asset_does_not_collapse_ambiguous_site() -> None:
    card = _card()
    card["facts"]["site"]["binding"] = {
        "status": "ambiguous",
        "id": None,
        "label": None,
        "candidates": [{"id": "S-MSK-01"}, {"id": "S-EKB-02"}],
    }
    apply_assets(
        card,
        [{"asset_id": "A-1001", "site_id": "S-MSK-01", "local_code": "ХУ-17"}],
    )
    assert card["facts"]["site"]["binding"]["status"] == "ambiguous"
    assert card["facts"]["asset"]["binding"]["status"] != "resolved"


def test_empty_search_keeps_mention() -> None:
    card = _card()
    card["facts"]["asset"]["mention"] = "КМ-9"
    apply_assets(card, [])
    assert card["facts"]["asset"]["mention"] == "КМ-9"
    assert card["facts"]["asset"]["binding"]["status"] == "not_found"


def test_one_ticket_fills_empty_slots() -> None:
    card = _card()
    apply_tickets(
        card,
        [
            {
                "ticket_id": "T-884",
                "customer_id": "C-101",
                "site_id": "S-MSK-01",
                "asset_id": "A-1001",
                "status": "in_progress",
                "summary": "ХУ-17",
            }
        ],
    )
    assert card["facts"]["history"]["binding"]["id"] == "T-884"
    assert card["facts"]["asset"]["binding"]["id"] == "A-1001"


def test_contract_resolved() -> None:
    card = _card()
    card["facts"]["site"]["binding"] = {
        "status": "resolved",
        "id": "S-MSK-01",
        "label": "Дмитровское",
        "candidates": [],
    }
    assert (
        apply_contract(
            card,
            [
                {
                    "contract_id": "K-101",
                    "site_id": "S-MSK-01",
                    "plan": "Gold",
                    "response_sla": "60_minutes",
                    "service_window": "24x7",
                    "coverage": ["repair"],
                }
            ],
        )
        == "resolved"
    )
    assert card["contract"]["id"] == "K-101"
