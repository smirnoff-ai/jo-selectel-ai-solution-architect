from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Index, Text
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Appeal(Base):
    __tablename__ = "appeals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('new', 'clarify', 'dispatch', 'approve', 'done')",
            name="appeals_status_check",
        ),
        CheckConstraint("run_status IN ('idle', 'running')", name="appeals_run_status_check"),
        CheckConstraint(
            "channel IN ('email', 'telegram', 'call', 'lk')",
            name="appeals_channel_check",
        ),
        Index("ix_appeals_status_received_at", "status", "received_at"),
        Index("ix_appeals_channel", "channel"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    run_status: Mapped[str] = mapped_column(Text, nullable=False, server_default="idle")
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(Text, nullable=False)
    card: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa_text("now()"),
    )
