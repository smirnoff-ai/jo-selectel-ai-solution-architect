from typing import Literal

from pydantic import BaseModel, Field

Outcome = Literal["create", "update", "clarify", "dispatch", "approve", "refuse_auto"]


class Finale(BaseModel):
    outcome: Outcome
    reason: str = Field(min_length=1)
    questions: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    reply_draft: str | None = None
    grounds: list[str] = Field(default_factory=list)
