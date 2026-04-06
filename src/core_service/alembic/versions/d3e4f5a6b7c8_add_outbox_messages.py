"""add outbox_messages table

Revision ID: d3e4f5a6b7c8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outbox_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
        sa.Column("routing_key", sa.String(128), nullable=False),
        sa.Column("exchange", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("published_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_outbox_messages_status", "outbox_messages", ["status"])


def downgrade() -> None:
    op.drop_index("ix_outbox_messages_status", table_name="outbox_messages")
    op.drop_table("outbox_messages")
