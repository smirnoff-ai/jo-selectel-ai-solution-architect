import json
import logging
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

Outcome = Literal["create", "update", "clarify", "dispatch", "approve", "refuse_auto"]


class Finale(BaseModel):
    outcome: Outcome = Field(
        description="Один исход: create, update, clarify, dispatch, approve, refuse_auto",
    )
    reason: str = Field(min_length=1, description="Коротко почему этот исход")
    questions: list[dict[str, object]] = Field(
        default_factory=list,
        description="Вопросы диспетчеру, если исход clarify",
    )
    warnings: list[dict[str, object]] = Field(
        default_factory=list,
        description="Предупреждения, например срок клиента раньше расчёта",
    )
    reply_draft: str | None = Field(
        default=None,
        description="Черновик ответа клиенту, не отправлять",
    )
    grounds: list[str] = Field(
        default_factory=list,
        description="Какие слоты карточки подтверждают исход",
    )


def message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "reasoning":
                    continue
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif block is not None:
                parts.append(str(block))
        return "".join(parts)
    return "" if content is None else str(content)


def parse_finale(content: object) -> Finale | None:
    text = message_text(content)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return Finale.model_validate(json.loads(text[start : end + 1]))
    except (json.JSONDecodeError, ValidationError):
        logger.info("finale parse missed")
        return None
