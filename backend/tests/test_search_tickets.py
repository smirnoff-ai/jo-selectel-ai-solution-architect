import json
from datetime import datetime

from backend.agent.run_context import RunContext, clear_run_context, set_run_context
from backend.agent.tools.search_tickets_tool import search_tickets
from backend.card_template import empty_card


class _FakeMock:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get(self, path: str, params: dict | None = None) -> tuple[int, dict]:
        self.calls.append((path, params or {}))
        return 200, {
            "items": [
                {
                    "ticket_id": "T-1",
                    "customer_id": "C-101",
                    "site_id": "S-1",
                    "asset_id": "A-1",
                    "contract_id": "K-1",
                    "status": "open",
                    "priority": "medium",
                    "summary": "Не охлаждает",
                    "created_at": "2026-08-13T10:00:00+03:00",
                    "updated_at": "2026-08-13T11:00:00+03:00",
                }
            ]
        }


def _ctx(mock: _FakeMock) -> RunContext:
    received_at = datetime.fromisoformat("2026-08-13T16:40:00+03:00")
    card = empty_card(
        channel="email",
        sender="СеверФуд",
        received_at=received_at,
        text="Склад",
        attachment_text=None,
    )
    return RunContext(appeal_id=1, card=card, mock=mock, received_at=received_at)


def test_search_tickets_without_identity_is_error() -> None:
    mock = _FakeMock()
    set_run_context(_ctx(mock))
    try:
        payload = json.loads(search_tickets.invoke({}))
    finally:
        clear_run_context()
    assert payload["status"] == "error"
    assert mock.calls == []
    assert "customer_id" in payload["next_actions"][0]


def test_search_tickets_customer_id_calls_catalog() -> None:
    mock = _FakeMock()
    set_run_context(_ctx(mock))
    try:
        payload = json.loads(search_tickets.invoke({"customer_id": "C-101"}))
    finally:
        clear_run_context()
    assert payload["status"] == "success"
    assert mock.calls == [("/itsm/v1/tickets", {"customer_id": "C-101", "status": "open"})]
    item = payload["result"]["items"][0]
    assert item["ticket_id"] == "T-1"
    assert item["summary"] == "Не охлаждает"
    assert item["created_at"]
