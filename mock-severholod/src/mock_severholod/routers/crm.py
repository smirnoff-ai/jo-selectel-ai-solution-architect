from typing import Annotated

from fastapi import APIRouter, Depends

from mock_severholod.deps import get_store
from mock_severholod.error_body import http_error
from mock_severholod.schemas import Site, SiteList
from mock_severholod.search_filters import SiteFilters
from mock_severholod.seed_store import SeedStore

router = APIRouter(prefix="/crm/v1")


@router.get("/sites")
async def search_sites(
    store: Annotated[SeedStore, Depends(get_store)],
    filters: Annotated[SiteFilters, Depends()],
) -> SiteList:
    if not filters.has_any():
        raise http_error(422, "Нужен хотя бы один параметр поиска", "validation")
    rows = store.search_sites(
        q=filters.q,
        customer_id=filters.customer_id,
        site_id=filters.site_id,
        customer_name=filters.customer_name,
        address=filters.address,
        timezone=filters.timezone,
    )
    return SiteList(items=[Site.model_validate(row) for row in rows])


@router.get("/sites/{site_id}")
async def get_site(site_id: str, store: Annotated[SeedStore, Depends(get_store)]) -> Site:
    row = store.get_site(site_id)
    if row is None:
        raise http_error(404, f"{site_id} not found", "not_found")
    return Site.model_validate(row)
