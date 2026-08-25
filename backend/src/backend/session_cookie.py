from hmac import compare_digest

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

COOKIE_NAME = "reflex_session"
MAX_AGE_SECONDS = 12 * 60 * 60


def sign_session(login: str, secret: str) -> str:
    return URLSafeTimedSerializer(secret).dumps({"login": login})


def read_session(token: str, secret: str) -> str | None:
    try:
        payload = URLSafeTimedSerializer(secret).loads(token, max_age=MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    login = payload.get("login")
    return login if isinstance(login, str) else None


def password_matches(given: str, expected: str) -> bool:
    return compare_digest(given.encode("utf-8"), expected.encode("utf-8"))
