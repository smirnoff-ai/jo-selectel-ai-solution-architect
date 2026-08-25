from fastapi import HTTPException
from fastapi.responses import JSONResponse


def error_payload(
    detail: str,
    code: str,
    checks: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {"detail": detail, "code": code, "checks": checks or []}


def http_error(status: int, detail: str, code: str) -> HTTPException:
    return HTTPException(status_code=status, detail=error_payload(detail, code))


def flk_response(checks: list[dict[str, object]], payload: dict[str, object]) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "persisted": False,
            "accepted": False,
            "would_ticket_id": None,
            "would_status": None,
            "payload": payload,
            "checks": checks,
            "detail": "Формально-логический контроль не пройден",
            "code": "flk_failed",
        },
    )
