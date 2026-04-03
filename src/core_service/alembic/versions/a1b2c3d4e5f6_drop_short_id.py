"""drop short_id from polls

Revision ID: a1b2c3d4e5f6
Revises: c6f9d552850f
Create Date: 2026-04-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c6f9d552850f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_polls_short_id", table_name="polls", if_exists=True)
    op.drop_column("polls", "short_id")


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column("polls", sa.Column("short_id", sa.String(16), nullable=True))
    op.create_index("ix_polls_short_id", "polls", ["short_id"], unique=True)
