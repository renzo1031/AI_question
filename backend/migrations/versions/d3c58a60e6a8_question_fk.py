"""Add foreign keys to Question table for Grade, Subject, and KnowledgePoint

Revision ID: d3c58a60e6a8
Revises: a4762acc2863
Create Date: 2025-12-25 13:07:46.972559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3c58a60e6a8'
down_revision: Union[str, None] = 'a4762acc2863'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加外键列
    op.add_column('questions', sa.Column('grade_id', sa.BigInteger(), nullable=True))
    op.add_column('questions', sa.Column('subject_id', sa.BigInteger(), nullable=True))
    op.add_column('questions', sa.Column('knowledge_point_id', sa.BigInteger(), nullable=True))
    
    # 创建索引
    op.create_index(op.f('ix_questions_grade_id'), 'questions', ['grade_id'], unique=False)
    op.create_index(op.f('ix_questions_subject_id'), 'questions', ['subject_id'], unique=False)
    op.create_index(op.f('ix_questions_knowledge_point_id'), 'questions', ['knowledge_point_id'], unique=False)
    
    # 创建外键约束
    op.create_foreign_key(
        'fk_questions_grade_id', 'questions', 'grades',
        ['grade_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_questions_subject_id', 'questions', 'subjects',
        ['subject_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_questions_knowledge_point_id', 'questions', 'knowledge_points',
        ['knowledge_point_id'], ['id'], ondelete='SET NULL'
    )
    
    # 删除旧的字符串字段的索引（如果存在）
    op.drop_index('ix_questions_grade', table_name='questions', if_exists=True)
    op.drop_index('ix_questions_knowledge_point', table_name='questions', if_exists=True)


def downgrade() -> None:
    # 恢复旧索引
    op.create_index('ix_questions_grade', 'questions', ['grade'], unique=False, if_not_exists=True)
    op.create_index('ix_questions_knowledge_point', 'questions', ['knowledge_point'], unique=False, if_not_exists=True)
    
    # 删除外键约束
    op.drop_constraint('fk_questions_knowledge_point_id', 'questions', type_='foreignkey')
    op.drop_constraint('fk_questions_subject_id', 'questions', type_='foreignkey')
    op.drop_constraint('fk_questions_grade_id', 'questions', type_='foreignkey')
    
    # 删除索引
    op.drop_index(op.f('ix_questions_knowledge_point_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_subject_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_grade_id'), table_name='questions')
    
    # 删除列
    op.drop_column('questions', 'knowledge_point_id')
    op.drop_column('questions', 'subject_id')
    op.drop_column('questions', 'grade_id')

