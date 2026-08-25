from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from backend.deps import get_settings, require_login
from backend.session_cookie import COOKIE_NAME, MAX_AGE_SECONDS, password_matches, sign_session
from backend.settings import Settings

router = APIRouter(prefix="/api/v1/auth")


class LoginBody(BaseModel):
    login: str
    password: str


class LoginOut(BaseModel):
    login: str


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        path="/",
    )


@router.post("/login")
async def login(
    body: LoginBody,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginOut:
    expected_login = settings.dispatcher_login
    expected_password = settings.dispatcher_password.get_secret_value()
    if body.login != expected_login or not password_matches(body.password, expected_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = sign_session(body.login, settings.session_secret.get_secret_value())
    _set_cookie(response, token)
    return LoginOut(login=body.login)


@router.post("/logout", status_code=204)
async def logout(response: Response, _login: Annotated[str, Depends(require_login)]) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me")
async def me(login: Annotated[str, Depends(require_login)]) -> LoginOut:
    return LoginOut(login=login)
