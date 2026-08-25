from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime
from typing import Any

from backend.agent.mock_http import MockHttp

_ID_KEYS = ("customer_id", "site_id", "asset_id", "ticket_id", "contract_id", "id")


class RunContext:
    def __init__(
        self,
        appeal_id: int,
        card: dict[str, Any],
        mock: MockHttp,
        received_at: datetime,
    ) -> None:
        self.appeal_id = appeal_id
        self.card = card
        self.mock = mock
        self.received_at = received_at
        self.catalog_errors: dict[str, int] = {}
        self.snapshots: list[dict[str, Any]] = []
        self.seen_ids: set[str] = set()
        self.last_calculation: dict[str, Any] | None = None

    def snapshot(self) -> None:
        self.snapshots.append(deepcopy(self.card))

    def note_error(self, catalog: str) -> int:
        self.catalog_errors[catalog] = self.catalog_errors.get(catalog, 0) + 1
        return self.catalog_errors[catalog]

    def remember_ids(self, items: list[dict[str, Any]]) -> None:
        for row in items:
            for key in _ID_KEYS:
                value = row.get(key)
                if isinstance(value, str) and value:
                    self.seen_ids.add(value)


_CTX: ContextVar[RunContext | None] = ContextVar("appeal_run", default=None)


def set_run_context(ctx: RunContext) -> None:
    _CTX.set(ctx)


def get_run_context() -> RunContext:
    ctx = _CTX.get()
    if ctx is None:
        msg = "нет контекста прогона"
        raise RuntimeError(msg)
    return ctx


def clear_run_context() -> None:
    _CTX.set(None)
