from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high", "critical"]
TicketStatus = Literal["new", "in_progress", "waiting_for_customer", "closed", "cancelled"]
OpenTicketStatus = Literal["new", "in_progress", "waiting_for_customer"]


class Site(BaseModel):
    site_id: str
    customer_id: str
    customer_name: str
    address: str
    timezone: str


class Asset(BaseModel):
    asset_id: str
    site_id: str
    local_code: str
    asset_type: str
    criticality: Literal["high", "medium"]


class Contract(BaseModel):
    contract_id: str
    site_id: str
    plan: str
    response_sla: Literal["60_minutes", "4_business_hours", "next_business_day"]
    service_window: Literal["24x7", "weekdays_09_18_local"]
    coverage: list[str]


class Ticket(BaseModel):
    ticket_id: str
    customer_id: str
    site_id: str
    asset_id: str | None
    contract_id: str
    status: TicketStatus
    priority: Priority
    summary: str
    created_at: str
    updated_at: str


class SiteList(BaseModel):
    items: list[Site]


class AssetList(BaseModel):
    items: list[Asset]


class ContractList(BaseModel):
    items: list[Contract]


class TicketList(BaseModel):
    items: list[Ticket]


class Health(BaseModel):
    status: Literal["ok"]


class Check(BaseModel):
    model_config = ConfigDict(exclude_none=True)

    id: str
    passed: bool
    detail: str | None = None


class TicketCreate(BaseModel):
    customer_id: str
    site_id: str
    contract_id: str
    summary: str
    priority: Priority
    asset_id: str | None = None


class TicketPatch(BaseModel):
    summary: str | None = None
    priority: Priority | None = None
    status: OpenTicketStatus | None = None
    customer_id: str | None = None
    site_id: str | None = None
    asset_id: str | None = None
    contract_id: str | None = None


class TicketWriteResult(BaseModel):
    persisted: bool
    accepted: bool
    would_ticket_id: str | None
    would_status: str | None
    payload: dict[str, object] = Field(default_factory=dict)
    checks: list[Check]
