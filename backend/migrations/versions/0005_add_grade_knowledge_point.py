"""add grade and knowledge_point to questions

Revision ID: 0005_add_grade_knowledge_point
Revises: 0004_user_admin_uuid
Create Date: 2025-12-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005_add_grade_knowledge_point"
down_revision = "0004_user_admin_uuid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 grade 和 knowledge_point 字段到 questions 表
    op.add_column('questions', sa.Column('grade', sa.String(length=50), nullable=True, comment='年级'))
    op.add_column('questions', sa.Column('knowledge_point', sa.String(length=200), nullable=True, comment='知识点'))
    
    # 创建索引以提高查询性能
    op.create_index('ix_questions_grade', 'questions', ['grade'], unique=False)
    op.create_index('ix_questions_knowledge_point', 'questions', ['knowledge_point'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_questions_knowledge_point', table_name='questions')
    op.drop_index('ix_questions_grade', table_name='questions')
    
    # 删除列
    op.drop_column('questions', 'knowledge_point')
    op.drop_column('questions', 'grade')
