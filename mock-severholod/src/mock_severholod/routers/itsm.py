from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from mock_severholod.deps import get_settings_dep, get_store
from mock_severholod.error_body import flk_response, http_error
from mock_severholod.schemas import Ticket, TicketCreate, TicketList, TicketPatch, TicketWriteResult
from mock_severholod.search_filters import TicketFilters
from mock_severholod.seed_store import SeedStore
from mock_severholod.settings import Settings
from mock_severholod.ticket_write import create_ticket, patch_ticket

router = APIRouter(prefix="/itsm/v1")


@router.get("/tickets")
async def search_tickets(
    store: Annotated[SeedStore, Depends(get_store)],
    filters: Annotated[TicketFilters, Depends()],
) -> TicketList:
    if not filters.has_identity():
        raise http_error(422, "Нужен хотя бы один идентификатор", "validation")
    rows = store.search_tickets(
        customer_id=filters.customer_id,
        site_id=filters.site_id,
        asset_id=filters.asset_id,
        contract_id=filters.contract_id,
        status=filters.status,
    )
    return TicketList(items=[Ticket.model_validate(row) for row in rows])


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, store: Annotated[SeedStore, Depends(get_store)]) -> Ticket:
    row = store.get_ticket(ticket_id)
    if row is None:
        raise http_error(404, f"{ticket_id} not found", "not_found")
    return Ticket.model_validate(row)


@router.post("/tickets", response_model=TicketWriteResult, response_model_exclude_none=True)
async def post_ticket(
    body: TicketCreate,
    store: Annotated[SeedStore, Depends(get_store)],
    cfg: Annotated[Settings, Depends(get_settings_dep)],
) -> JSONResponse | TicketWriteResult:
    ok, result = create_ticket(
        store,
        body.model_dump(),
        persist=cfg.allow_ticket_mutations,
    )
    if not ok:
        return flk_response(list(result["checks"]), dict(result["payload"]))
    return TicketWriteResult.model_validate(result)


@router.patch(
    "/tickets/{ticket_id}",
    response_model=TicketWriteResult,
    response_model_exclude_none=True,
)
async def patch_ticket_route(
    ticket_id: str,
    body: TicketPatch,
    store: Annotated[SeedStore, Depends(get_store)],
    cfg: Annotated[Settings, Depends(get_settings_dep)],
) -> JSONResponse | TicketWriteResult:
    ok, result = patch_ticket(
        store,
        ticket_id,
        body.model_dump(),
        persist=cfg.allow_ticket_mutations,
    )
    if not ok:
        return flk_response(list(result["checks"]), dict(result["payload"]))
    return TicketWriteResult.model_validate(result)
