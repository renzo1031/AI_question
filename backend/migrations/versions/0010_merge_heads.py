"""merge multiple heads

Revision ID: 0010_merge_heads
Revises: 0009_add_banners_table, 4595591b5d67
Create Date: 2026-02-23

"""
from typing import Sequence, Union

revision: str = "0010_merge_heads"
down_revision: Union[str, tuple] = ("0009_add_banners_table", "4595591b5d67")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
