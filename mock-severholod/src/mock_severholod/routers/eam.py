from typing import Annotated

from fastapi import APIRouter, Depends

from mock_severholod.deps import get_store
from mock_severholod.error_body import http_error
from mock_severholod.schemas import Asset, AssetList
from mock_severholod.search_filters import AssetFilters
from mock_severholod.seed_store import SeedStore

router = APIRouter(prefix="/eam/v1")


@router.get("/assets")
async def search_assets(
    store: Annotated[SeedStore, Depends(get_store)],
    filters: Annotated[AssetFilters, Depends()],
) -> AssetList:
    if not filters.has_any():
        raise http_error(422, "Нужен хотя бы один параметр поиска", "validation")
    rows = store.search_assets(
        q=filters.q,
        asset_id=filters.asset_id,
        site_id=filters.site_id,
        local_code=filters.local_code,
        asset_type=filters.asset_type,
        criticality=filters.criticality,
    )
    return AssetList(items=[Asset.model_validate(row) for row in rows])


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str, store: Annotated[SeedStore, Depends(get_store)]) -> Asset:
    row = store.get_asset(asset_id)
    if row is None:
        raise http_error(404, f"{asset_id} not found", "not_found")
    return Asset.model_validate(row)
