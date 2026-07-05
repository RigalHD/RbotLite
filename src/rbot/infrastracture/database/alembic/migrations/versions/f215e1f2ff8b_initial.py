"""initial

Revision ID: f215e1f2ff8b
Revises: 
Create Date: 2026-07-05 13:12:14.495187
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'f215e1f2ff8b'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
