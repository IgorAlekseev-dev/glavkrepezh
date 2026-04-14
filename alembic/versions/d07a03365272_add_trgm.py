"""add trgm

Revision ID: d07a03365272
Revises: 9ca1d61967e8
Create Date: 2026-02-21 15:47:42.530888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd07a03365272'
down_revision: Union[str, Sequence[str], None] = '9ca1d61967e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS pg_trgm')
