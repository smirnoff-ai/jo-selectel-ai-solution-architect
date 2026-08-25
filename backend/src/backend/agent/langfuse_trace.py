import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend.settings import Settings

logger = logging.getLogger(__name__)


def make_callback(settings: Settings, _appeal_id: int) -> Any | None:
    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler
    except ImportError:
        logger.exception("langfuse callback import")
        return None
    try:
        Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            host=settings.langfuse_host,
        )
        return CallbackHandler()
    except (OSError, RuntimeError, TypeError, ValueError):
        logger.exception("langfuse callback")
        return None


async def traced_invoke[T](
    appeal_id: int,
    body: Callable[[], Awaitable[T]],
) -> T:
    try:
        from langfuse import propagate_attributes
    except ImportError:
        logger.exception("langfuse propagate")
        return await body()
    with propagate_attributes(
        trace_name="reflex-appeal",
        session_id=str(appeal_id),
        metadata={"appeal_id": str(appeal_id)},
    ):
        return await body()


def flush_callback(_handler: Any | None) -> None:
    try:
        from langfuse import get_client
    except ImportError:
        return
    try:
        get_client().flush()
    except (OSError, RuntimeError):
        logger.exception("langfuse flush")
