"""Аргументы тула calculate. В карточку не ходит."""

from typing import Literal

from pydantic import BaseModel, Field

Criticality = Literal["low", "medium", "high"]
Priority = Literal["low", "medium", "high", "critical"]
SlaCode = Literal["60_minutes", "4_business_hours", "next_business_day"]


class CalculateInput(BaseModel):
    model_config = {"extra": "forbid"}

    asset_criticality: Criticality | None = Field(
        default=None,
        description="Критичность оборудования из ответа поиска оборудования",
    )
    symptoms_text: str = Field(
        default="",
        description="Симптомы и суть поломки из письма, как есть",
    )
    open_ticket_priority: Priority | None = Field(
        default=None,
        description="Приоритет открытой заявки, если нашли. Не передавай — ветка создания",
    )
    response_sla: SlaCode | None = Field(
        default=None,
        description="Код срока ответа с договора",
    )
    service_window: str | None = Field(
        default=None,
        description="Окно обслуживания с договора",
    )
    timezone: str | None = Field(
        default=None,
        description="Часовой пояс площадки из ответа поиска площадок",
    )
