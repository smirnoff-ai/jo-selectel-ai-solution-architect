"""appeals tables

Revision ID: 0001appeals
Revises:
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001appeals"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE appeals (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            status TEXT NOT NULL CHECK (status IN ('new', 'clarify', 'dispatch', 'approve', 'done')),
            run_status TEXT NOT NULL DEFAULT 'idle' CHECK (run_status IN ('idle', 'running')),
            channel TEXT NOT NULL CHECK (channel IN ('email', 'telegram', 'call', 'lk')),
            sender TEXT NULL,
            received_at TIMESTAMPTZ NOT NULL,
            text TEXT NOT NULL,
            attachment_text TEXT NULL,
            created_by TEXT NOT NULL,
            card JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_appeals_status_received_at ON appeals (status, received_at DESC);
        CREATE INDEX ix_appeals_channel ON appeals (channel);

        CREATE TABLE appeal_messages (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            appeal_id BIGINT NOT NULL REFERENCES appeals(id) ON DELETE CASCADE,
            author TEXT NOT NULL,
            kind TEXT NOT NULL,
            body JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_appeal_messages_appeal_created ON appeal_messages (appeal_id, created_at);

        CREATE TABLE appeal_events (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            appeal_id BIGINT NOT NULL REFERENCES appeals(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            card_snapshot JSONB NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_appeal_events_appeal_created ON appeal_events (appeal_id, created_at);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS appeal_events;")
    op.execute("DROP TABLE IF EXISTS appeal_messages;")
    op.execute("DROP TABLE IF EXISTS appeals;")
