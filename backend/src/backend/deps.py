from fastapi import HTTPException, Request

from backend.session_cookie import COOKIE_NAME, read_session
from backend.settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def require_login(request: Request) -> str:
    settings: Settings = request.app.state.settings
    token = request.cookies.get(COOKIE_NAME)
    if token is None:
        raise HTTPException(status_code=401, detail="Нет сессии")
    login = read_session(token, settings.session_secret.get_secret_value())
    if login is None or login != settings.dispatcher_login:
        raise HTTPException(status_code=401, detail="Нет сессии")
    return login
