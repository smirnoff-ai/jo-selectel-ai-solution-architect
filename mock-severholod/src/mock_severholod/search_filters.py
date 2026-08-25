from pydantic import BaseModel, Field


class SiteFilters(BaseModel):
    q: str | None = None
    customer_id: str | None = None
    site_id: str | None = None
    customer_name: str | None = None
    address: str | None = None
    timezone: str | None = None

    def has_any(self) -> bool:
        return any(
            (
                self.q,
                self.customer_id,
                self.site_id,
                self.customer_name,
                self.address,
                self.timezone,
            )
        )


class AssetFilters(BaseModel):
    q: str | None = None
    asset_id: str | None = None
    site_id: str | None = None
    local_code: str | None = None
    asset_type: str | None = None
    criticality: str | None = None

    def has_any(self) -> bool:
        return any(
            (
                self.q,
                self.asset_id,
                self.site_id,
                self.local_code,
                self.asset_type,
                self.criticality,
            )
        )


class TicketFilters(BaseModel):
    customer_id: str | None = None
    site_id: str | None = None
    asset_id: str | None = None
    contract_id: str | None = None
    status: str | None = None

    def has_identity(self) -> bool:
        return any((self.customer_id, self.site_id, self.asset_id, self.contract_id))


class ContractFilters(BaseModel):
    site_id: str = Field(...)
