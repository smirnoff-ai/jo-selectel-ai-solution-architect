import json
from typing import Any

from backend.models.appeal import Appeal


def build_user_message(appeal: Appeal, reply_text: str | None) -> str:
    parts = [
        f"appeal_id={appeal.id}",
        f"Канал: {appeal.channel}",
        f"Отправитель: {appeal.sender or 'не указан'}",
        f"Получено: {appeal.received_at.isoformat()}",
        f"Текст:\n{appeal.text}",
    ]
    if appeal.attachment_text:
        parts.append(f"Вложение:\n{appeal.attachment_text}")
    if reply_text:
        parts.append(f"Реплика диспетчера:\n{reply_text}")
    card: dict[str, Any] = appeal.card
    parts.append("Актуальный card:\n" + json.dumps(card, ensure_ascii=False))
    return "\n\n".join(parts)
