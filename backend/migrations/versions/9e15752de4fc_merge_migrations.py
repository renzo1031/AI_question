"""merge migrations

Revision ID: 9e15752de4fc
Revises: 0008_system_configs, d3c58a60e6a8
Create Date: 2025-12-25 16:33:32.556802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e15752de4fc'
down_revision: Union[str, None] = ('0008_system_configs', 'd3c58a60e6a8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

