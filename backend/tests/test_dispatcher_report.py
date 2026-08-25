from datetime import datetime

from backend.agent.dispatcher_report import (
    attach_report_if_missing,
    build_dispatcher_report,
    persist_has_message_final,
    tool_names_from_persist,
)
from backend.card_template import empty_card


def _card() -> dict:
    return empty_card(
        channel="email",
        sender="СеверФуд",
        received_at=datetime.fromisoformat("2026-08-13T16:40:00+03:00"),
        text="Склад, установка не запускается",
        attachment_text=None,
    )


def test_clarify_report_has_questions_and_found_slots() -> None:
    card = _card()
    card["facts"]["customer"]["binding"] = {
        "status": "resolved",
        "id": "C-101",
        "label": "СеверФуд",
        "candidates": [],
    }
    card["facts"]["site"]["binding"] = {
        "status": "ambiguous",
        "id": None,
        "label": None,
        "candidates": [
            {"id": "S-MSK-01", "label": "Москва, Дмитровское"},
            {"id": "S-EKB-01", "label": "Екатеринбург, Монтажников"},
        ],
    }
    card["facts"]["problem"]["value"] = "не охлаждает"
    card["decision"] = {
        "outcome": "clarify",
        "reason": "Две площадки, выбрать нельзя",
        "questions": [{"text": "Какой объект: Москва или Екатеринбург?"}],
        "warnings": [{"code": "sla", "text": "Срок клиента раньше расчёта"}],
        "reply_draft": "Уточните площадку, пожалуйста.",
    }
    text = build_dispatcher_report(
        card,
        tool_names=["search_sites", "update_card", "search_assets", "update_card"],
    )
    assert "## Нужно уточнение" in text
    assert "Две площадки, выбрать нельзя" in text
    assert "поиск площадок" in text
    assert "СеверФуд (`C-101`)" in text
    assert "Москва, Дмитровское / Екатеринбург, Монтажников" in text
    assert "не охлаждает" in text
    assert "1. Какой объект: Москва или Екатеринбург?" in text
    assert "sla: Срок клиента раньше расчёта" in text
    assert "Уточните площадку, пожалуйста." in text


def test_create_report_covers_contract_calc_and_dry_run() -> None:
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
        "label": "Москва, Дмитровское шоссе, 100",
        "candidates": [],
    }
    card["contract"] = {
        "status": "resolved",
        "id": "К-101",
        "plan": "стандарт",
        "response_sla": "4_business_hours",
    }
    card["calculation"] = {
        "status": "computed",
        "priority": {"value": "low"},
        "sla": {"code": "4_business_hours"},
        "deadline": {"at": "2026-08-14T12:00:00+03:00"},
    }
    card["decision"] = {
        "outcome": "create",
        "reason": "Клиент и площадка однозначны, открытой заявки нет",
        "questions": [],
        "warnings": [],
        "itsm_dry_run": {"accepted": True, "would_ticket_id": "T-9001"},
    }
    text = build_dispatcher_report(card, tool_names=["get_contract", "calculate", "update_card"])
    assert "## Создать заявку" in text
    assert "К-101" in text
    assert "4 рабочих часа" in text
    assert "приоритет низкий" in text
    assert "14.08.2026 12:00" in text
    assert "сухой прогон создания" in text.lower()
    assert "T-9001" in text


def test_attach_report_if_missing_for_old_runs() -> None:
    card = _card()
    card["decision"]["outcome"] = "clarify"
    card["decision"]["reason"] = "Две площадки"
    items = [{"id": 3, "author": "agent", "kind": "tool_result", "body": {"name": "search_sites"}}]
    attached = attach_report_if_missing(
        card,
        items,
        tool_names=["search_sites"],
        message_id=4,
        created_at="2026-08-13T16:50:00+03:00",
    )
    assert attached[-1]["id"] == 4
    assert attached[-1]["kind"] == "message"
    assert "## Нужно уточнение" in attached[-1]["body"]["text"]
    same = attach_report_if_missing(
        card,
        attached,
        tool_names=["search_sites"],
        message_id=5,
        created_at="2026-08-13T16:50:00+03:00",
    )
    assert same == attached


def test_persist_helpers() -> None:
    persist = [
        {"type": "tool_result", "name": "search_sites"},
        {"type": "tool_result", "name": "update_card"},
        {"type": "message_final", "text": "  "},
    ]
    assert persist_has_message_final(persist) is False
    assert tool_names_from_persist(persist) == ["search_sites", "update_card"]
    persist.append({"type": "message_final", "text": "Итог"})
    assert persist_has_message_final(persist) is True
