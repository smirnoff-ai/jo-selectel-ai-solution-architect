from typing import Annotated

from fastapi import APIRouter, Depends

from mock_severholod.deps import get_store
from mock_severholod.error_body import http_error
from mock_severholod.schemas import Contract, ContractList
from mock_severholod.search_filters import ContractFilters
from mock_severholod.seed_store import SeedStore

router = APIRouter(prefix="/contracts/v1")


@router.get("/contracts")
async def search_contracts(
    store: Annotated[SeedStore, Depends(get_store)],
    filters: Annotated[ContractFilters, Depends()],
) -> ContractList:
    rows = store.search_contracts(filters.site_id)
    return ContractList(items=[Contract.model_validate(row) for row in rows])


@router.get("/contracts/{contract_id}")
async def get_contract(
    contract_id: str,
    store: Annotated[SeedStore, Depends(get_store)],
) -> Contract:
    row = store.get_contract(contract_id)
    if row is None:
        raise http_error(404, f"{contract_id} not found", "not_found")
    return Contract.model_validate(row)
