"""Аргументы тула patch_facts. Канон: docs/requirements/severholod/schemas/patch_facts.py."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Kind = Literal["fact", "assumption", "system"]
Source = Literal[
    "intake_text",
    "intake_sender",
    "intake_attachment",
    "dispatcher",
    "crm",
    "eam",
    "contract",
    "itsm",
]
Confidence = Literal["high", "medium", "low"]
SystemName = Literal["crm", "eam", "contract", "itsm"]


class RecordRef(BaseModel):
    model_config = {"extra": "forbid"}

    system: SystemName
    id: str = Field(description="Id записи из ответа только что вызванного поиска")
    label: str | None = Field(default=None, description="Короткая подпись")


class EvidencePatch(BaseModel):
    model_config = {"extra": "forbid"}

    kind: Kind
    source: Source
    fragment: str | None = Field(default=None)
    record: RecordRef | None = Field(default=None)
    confidence: Confidence

    @model_validator(mode="after")
    def kind_matches_fields(self) -> EvidencePatch:
        if self.kind == "fact":
            if not self.fragment:
                raise ValueError("fact требует fragment")
            if self.record is not None:
                raise ValueError("fact не несёт record")
            if self.source not in (
                "intake_text",
                "intake_sender",
                "intake_attachment",
                "dispatcher",
            ):
                raise ValueError("fact только из входа или реплики диспетчера")
        if self.kind == "assumption" and self.record is not None:
            raise ValueError("assumption не несёт record")
        if self.kind == "system":
            if self.record is None:
                raise ValueError("system требует record")
            if self.fragment is not None:
                raise ValueError("system без fragment письма")
            if self.source not in ("crm", "eam", "contract", "itsm"):
                raise ValueError("system.source должен быть справочник")
            if self.source != self.record.system:
                raise ValueError("source и record.system должны совпадать")
        return self


class IdentityFactPatch(BaseModel):
    model_config = {"extra": "forbid"}

    mention: str | None = Field(default=None)
    evidences: list[EvidencePatch] = Field(default_factory=list)


class NarrativeFactPatch(BaseModel):
    model_config = {"extra": "forbid"}

    value: str | None = None
    evidences: list[EvidencePatch] = Field(default_factory=list)


class PatchFactsInput(BaseModel):
    model_config = {"extra": "forbid"}

    customer: IdentityFactPatch | None = None
    site: IdentityFactPatch | None = None
    asset: IdentityFactPatch | None = None
    history: IdentityFactPatch | None = None
    problem: NarrativeFactPatch | None = None
    symptoms: NarrativeFactPatch | None = None
    desired_deadline: NarrativeFactPatch | None = None
    backup: NarrativeFactPatch | None = None

    @model_validator(mode="after")
    def at_least_one_slot(self) -> PatchFactsInput:
        slots = (
            self.customer,
            self.site,
            self.asset,
            self.history,
            self.problem,
            self.symptoms,
            self.desired_deadline,
            self.backup,
        )
        if all(slot is None for slot in slots):
            raise ValueError("нужен хотя бы один слот")
        return self
