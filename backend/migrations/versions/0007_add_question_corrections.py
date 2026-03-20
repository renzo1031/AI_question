"""add question corrections table

Revision ID: 0007
Revises: 0006
Create Date: 2025-12-26 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, None] = '0006_add_subjects'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建纠错表
    op.create_table(
        'question_corrections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='纠错记录ID'),
        sa.Column('question_id', sa.BigInteger(), nullable=False, comment='题目ID'),
        sa.Column('user_id', postgresql.UUID(), nullable=True, comment='提交用户ID'),
        sa.Column('reason', sa.Text(), nullable=True, comment='纠错原因/描述'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='状态：pending(待处理)/resolved(已解决)/ignored(已忽略)'),
        sa.Column('admin_note', sa.Text(), nullable=True, comment='管理员备注'),
        sa.Column('handled_by', postgresql.UUID(), nullable=True, comment='处理人ID'),
        sa.Column('handled_at', sa.DateTime(timezone=True), nullable=True, comment='处理时间'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_question_corrections_question_id', 'question_corrections', ['question_id'])
    op.create_index('ix_question_corrections_user_id', 'question_corrections', ['user_id'])
    op.create_index('ix_question_corrections_status', 'question_corrections', ['status'])
    
    # 创建外键
    op.create_foreign_key(
        'fk_question_corrections_question_id',
        'question_corrections', 'questions',
        ['question_id'], ['id'],
        ondelete='CASCADE'
    )
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
    op.drop_constraint('fk_question_corrections_question_id', 'question_corrections', type_='foreignkey')
    
    # 删除索引
    op.drop_index('ix_question_corrections_status', 'question_corrections')
    op.drop_index('ix_question_corrections_user_id', 'question_corrections')
    op.drop_index('ix_question_corrections_question_id', 'question_corrections')
    
    # 删除表
    op.drop_table('question_corrections')
