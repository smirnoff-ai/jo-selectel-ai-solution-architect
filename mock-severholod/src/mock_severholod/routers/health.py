from fastapi import APIRouter

from mock_severholod.schemas import Health

router = APIRouter()


@router.get("/health")
async def health() -> Health:
    return Health(status="ok")
