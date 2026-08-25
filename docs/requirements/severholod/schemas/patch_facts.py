"""Аргументы тула patch_facts. Канон схемы для первой версии.

Поле binding сюда не входит: id после поиска пишет тело search_*.
Опущенный слот не трогаем. Пустой объект слота тоже не затирает карточку.
"""

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
    label: str | None = Field(default=None, description="Короткая подпись: адрес, код, тема тикета")


class EvidencePatch(BaseModel):
    model_config = {"extra": "forbid"}

    kind: Kind
    source: Source
    fragment: str | None = Field(
        default=None,
        description="Прямая цитата. Обязательна для kind=fact, иначе null",
    )
    record: RecordRef | None = Field(
        default=None,
        description="Ссылка на запись системы. Обязательна для kind=system",
    )
    confidence: Confidence

    @model_validator(mode="after")
    def kind_matches_fields(self) -> EvidencePatch:
        if self.kind == "fact":
            if not self.fragment:
                msg = "fact требует fragment"
                raise ValueError(msg)
            if self.record is not None:
                msg = "fact не несёт record"
                raise ValueError(msg)
            if self.source not in (
                "intake_text",
                "intake_sender",
                "intake_attachment",
                "dispatcher",
            ):
                msg = "fact только из входа или реплики диспетчера"
                raise ValueError(msg)
        if self.kind == "assumption" and self.record is not None:
            msg = "assumption не несёт record"
            raise ValueError(msg)
        if self.kind == "system":
            if self.record is None:
                msg = "system требует record"
                raise ValueError(msg)
            if self.fragment is not None:
                msg = "system без fragment письма"
                raise ValueError(msg)
            if self.source not in ("crm", "eam", "contract", "itsm"):
                msg = "system.source должен быть справочник"
                raise ValueError(msg)
            if self.source != self.record.system:
                msg = "source и record.system должны совпадать"
                raise ValueError(msg)
        return self


class IdentityFactPatch(BaseModel):
    """Клиент, объект, оборудование, прошлое обращение. Без binding."""

    model_config = {"extra": "forbid"}

    mention: str | None = Field(default=None, description="Как сказали в тексте, не id")
    evidences: list[EvidencePatch] = Field(default_factory=list)


class NarrativeFactPatch(BaseModel):
    """Проблема, симптомы, срок, резерв. Без parsed_at."""

    model_config = {"extra": "forbid"}

    value: str | None = None
    evidences: list[EvidencePatch] = Field(default_factory=list)


class PatchFactsInput(BaseModel):
    """Вход тула patch_facts. Все слоты необязательны."""

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
            msg = "нужен хотя бы один слот"
            raise ValueError(msg)
        return self
