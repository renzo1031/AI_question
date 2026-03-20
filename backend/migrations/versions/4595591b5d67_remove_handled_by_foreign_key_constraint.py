"""remove handled_by foreign key constraint - admins are not in users table

Revision ID: 4595591b5d67
Revises:
Create Date: 2025-12-26 17:39:39.243118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4595591b5d67'
down_revision: Union[str, None] = '8e836a7c5d0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 删除 handled_by 的外键约束，因为管理员不在 users 表中
    op.drop_constraint('fk_question_corrections_handled_by', 'question_corrections', type_='foreignkey')


def downgrade() -> None:
    # 恢复外键约束（但这会导致问题，因为 admins 不在 users 表中）
    from sqlalchemy.dialects import postgresql
    op.create_foreign_key(
        'fk_question_corrections_handled_by',
        'question_corrections', 'users',
        ['handled_by'], ['id'],
        ondelete='SET NULL'
    )

