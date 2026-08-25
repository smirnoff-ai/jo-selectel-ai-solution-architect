from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from backend.agent.mock_http import MockHttp


@dataclass
class RunContext:
    appeal_id: int
    card: dict[str, Any]
    mock: MockHttp
    catalog_errors: dict[str, int] = field(default_factory=dict)
    snapshots: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> None:
        self.snapshots.append(deepcopy(self.card))

    def note_error(self, catalog: str) -> int:
        self.catalog_errors[catalog] = self.catalog_errors.get(catalog, 0) + 1
        return self.catalog_errors[catalog]


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
