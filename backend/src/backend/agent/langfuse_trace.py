import logging

from langfuse import Langfuse

from backend.settings import Settings

logger = logging.getLogger(__name__)


def make_langfuse(settings: Settings) -> Langfuse | None:
    try:
        return Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            host=settings.langfuse_host,
            timeout=2,
        )
    except Exception:
        logger.exception("langfuse client")
        return None
