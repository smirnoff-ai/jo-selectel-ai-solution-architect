"""Аргументы тула update_card. Канон: docs/requirements/severholod/schemas/update_card.py.

Опущенный слот не трогаем. Привязку и договор пишет агент после поиска.
Расчёт принимается только как намерение записать последний ответ calculate.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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
BindingStatus = Literal["empty", "mentioned", "resolved", "not_found", "ambiguous"]
ContractStatus = Literal["empty", "resolved", "not_found"]
Outcome = Literal["create", "update", "clarify", "dispatch", "approve", "refuse_auto"]


class RecordRef(BaseModel):
    model_config = {"extra": "forbid"}

    system: SystemName = Field(
        description="Справочник, из которого только что пришёл идентификатор",
    )
    id: str = Field(description="Идентификатор из result последнего поиска, не из письма")
    label: str | None = Field(
        default=None,
        description="Короткая подпись из ответа поиска: адрес, код установки, тема заявки",
    )


class EvidencePatch(BaseModel):
    model_config = {"extra": "forbid"}

    kind: Kind = Field(description="fact — цитата из письма; system — идентификатор из поиска")
    source: Source = Field(
        description="Откуда факт: письмо, отправитель, вложение, диспетчер либо справочник",
    )
    fragment: str | None = Field(
        default=None,
        description="Прямая цитата. Обязательна для kind=fact, для system не передавай",
    )
    record: RecordRef | None = Field(
        default=None,
        description="Ссылка на запись справочника. Обязательна для kind=system",
    )
    confidence: Confidence = Field(
        description="high — явно в тексте; medium или low — домысливание",
    )

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


def _parse_json_value(value: object) -> object:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or text[0] not in "{[":
        return value
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value


class CandidatePatch(BaseModel):
    model_config = {"extra": "forbid"}

    id: str = Field(description="Идентификатор из ответа поиска")
    label: str | None = Field(default=None, description="Подпись из ответа поиска")
    site_id: str | None = Field(default=None, description="Площадка кандидата, если есть")
    customer_id: str | None = Field(default=None, description="Клиент кандидата, если есть")


class BindingPatch(BaseModel):
    model_config = {"extra": "forbid"}

    status: BindingStatus = Field(description="empty, mentioned, resolved, not_found или ambiguous")
    id: str | None = Field(
        default=None,
        description="Идентификатор при resolved, иначе не передавай",
    )
    label: str | None = Field(default=None, description="Подпись записи из ответа поиска")
    candidates: list[CandidatePatch] = Field(
        default_factory=list,
        description="Список при ambiguous: идентификатор и подпись каждой записи",
    )


class IdentityFactPatch(BaseModel):
    """Клиент, площадка, оборудование или прошлое обращение."""

    model_config = {"extra": "forbid"}

    mention: str | None = Field(
        default=None,
        description="Как сказали в письме, не идентификатор справочника",
    )
    binding: BindingPatch | None = Field(
        default=None,
        description="Привязка к записи справочника. Ставь после поиска, не до него",
    )
    evidences: list[EvidencePatch] = Field(default_factory=list)


class NarrativeFactPatch(BaseModel):
    """Проблема, симптомы, желаемый срок, резерв."""

    model_config = {"extra": "forbid"}

    value: str | None = Field(default=None, description="Свободная формулировка, как в письме")
    evidences: list[EvidencePatch] = Field(default_factory=list)


class ContractPatch(BaseModel):
    model_config = {"extra": "forbid"}

    status: ContractStatus = Field(description="empty, resolved или not_found")
    id: str | None = Field(default=None, description="Идентификатор договора из get_contract")
    site_id: str | None = Field(
        default=None,
        description="Площадка, для которой спрашивали договор",
    )
    plan: str | None = Field(default=None, description="Тарифный план из ответа")
    response_sla: str | None = Field(default=None, description="Код срока ответа из ответа")
    service_window: str | None = Field(default=None, description="Окно обслуживания из ответа")
    coverage: list[str] = Field(default_factory=list, description="Покрытие из ответа")


class DecisionPatch(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: Outcome | None = Field(default=None, description="Один исход разбора")
    reason: str | None = Field(default=None, description="Почему этот исход")
    grounds: list[str] | None = Field(default=None, description="Какие слоты держат исход")
    questions: list[dict[str, Any]] | None = Field(default=None, description="Вопросы диспетчеру")
    warnings: list[dict[str, Any]] | None = Field(default=None, description="Предупреждения")
    reply_draft: str | None = Field(
        default=None,
        description="Черновик ответа клиенту, не отправлять",
    )


class UpdateCardInput(BaseModel):
    """Поля карточки. Передай только те, что меняешь. Пустой вызов нельзя."""

    model_config = {"extra": "forbid"}

    customer: IdentityFactPatch | None = Field(
        default=None,
        description="Организация-клиент, не имя человека из подписи",
    )
    site: IdentityFactPatch | None = Field(
        default=None,
        description="Площадка или адрес объекта",
    )
    asset: IdentityFactPatch | None = Field(
        default=None,
        description="Оборудование: код или тип установки, как написали",
    )
    history: IdentityFactPatch | None = Field(
        default=None,
        description="Упоминание уже открытой заявки, если оно есть в письме",
    )
    problem: NarrativeFactPatch | None = Field(default=None, description="Суть поломки")
    symptoms: NarrativeFactPatch | None = Field(default=None, description="Наблюдаемые симптомы")
    desired_deadline: NarrativeFactPatch | None = Field(
        default=None,
        description="Желаемый срок визита словами клиента",
    )
    backup: NarrativeFactPatch | None = Field(
        default=None,
        description="Есть ли резерв, куда перенесли товар",
    )
    contract: ContractPatch | None = Field(
        default=None,
        description="Договор площадки из ответа get_contract",
    )
    calculation: dict[str, Any] | None = Field(
        default=None,
        description="Объект из result.calculation последнего calculate. Свои цифры не принимаются",
    )
    decision: DecisionPatch | None = Field(
        default=None,
        description="Исход и пояснение для диспетчера",
    )

    @field_validator(
        "customer",
        "site",
        "asset",
        "history",
        mode="before",
    )
    @classmethod
    def coerce_identity(cls, value: object) -> object:
        parsed = _parse_json_value(value)
        if isinstance(parsed, str):
            return {"mention": parsed}
        return parsed

    @field_validator(
        "problem",
        "symptoms",
        "desired_deadline",
        "backup",
        mode="before",
    )
    @classmethod
    def coerce_narrative(cls, value: object) -> object:
        parsed = _parse_json_value(value)
        if isinstance(parsed, str):
            return {"value": parsed}
        return parsed

    @field_validator("contract", "decision", "calculation", mode="before")
    @classmethod
    def coerce_object(cls, value: object) -> object:
        return _parse_json_value(value)

    @model_validator(mode="after")
    def at_least_one_field(self) -> UpdateCardInput:
        fields = (
            self.customer,
            self.site,
            self.asset,
            self.history,
            self.problem,
            self.symptoms,
            self.desired_deadline,
            self.backup,
            self.contract,
            self.calculation,
            self.decision,
        )
        if all(item is None for item in fields):
            msg = "нужно хотя бы одно поле карточки"
            raise ValueError(msg)
        return self
