"""fix question_corrections uuid columns - convert VARCHAR to UUID

Revision ID: 8e836a7c5d0a
Revises: 92fab52a74f2
Create Date:

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8e836a7c5d0a'
down_revision: Union[str, None] = '92fab52a74f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 先删除外键约束
    op.drop_constraint('fk_question_corrections_user_id', 'question_corrections', type_='foreignkey')
    op.drop_constraint('fk_question_corrections_handled_by', 'question_corrections', type_='foreignkey')
    
    # 将 VARCHAR 列改为 UUID 类型
    op.alter_column('question_corrections', 'user_id',
                    type_=postgresql.UUID(),
                    postgresql_using='user_id::uuid',
                    existing_nullable=True)
    op.alter_column('question_corrections', 'handled_by',
                    type_=postgresql.UUID(),
                    postgresql_using='handled_by::uuid',
                    existing_nullable=True)
    
    # 重新创建外键
    op.create_foreign_key(
        'fk_question_corrections_user_id',
        'question_corrections', 'users',
        ['user_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_question_corrections_handled_by',
        'question_corrections', 'users',
        ['handled_by'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # 删除外键
    op.drop_constraint('fk_question_corrections_handled_by', 'question_corrections', type_='foreignkey')
    op.drop_constraint('fk_question_corrections_user_id', 'question_corrections', type_='foreignkey')
    
    # 将 UUID 列改回 VARCHAR
    op.alter_column('question_corrections', 'user_id',
                    type_=sa.String(36),
                    postgresql_using='user_id::varchar',
                    existing_nullable=True)
    op.alter_column('question_corrections', 'handled_by',
                    type_=sa.String(36),
                    postgresql_using='handled_by::varchar',
                    existing_nullable=True)
    
    # 重新创建外键
    op.create_foreign_key(
        'fk_question_corrections_user_id',
        'question_corrections', 'users',
        ['user_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_question_corrections_handled_by',
        'question_corrections', 'users',
        ['handled_by'], ['id'],
        ondelete='SET NULL'
    )

