"""convert_tags_to_sub_knowledge_points

Revision ID: a4762acc2863
Revises: a6dac05e93c3
Create Date: 2025-12-24 18:56:30.757539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4762acc2863'
down_revision: Union[str, None] = 'a6dac05e93c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    将标签表（tags）转换为次知识点表
    1. 添加 knowledge_point_id 和 sort_order 字段
    2. 删除 parent_id 和 level 字段
    3. 修改外键关系
    """
    # 删除旧的外键约束
    op.execute('ALTER TABLE tags DROP CONSTRAINT IF EXISTS tags_parent_id_fkey')
    
    # 删除旧的索引
    op.execute('DROP INDEX IF EXISTS ix_tags_parent_id')
    
    # 添加新字段
    op.execute('ALTER TABLE tags ADD COLUMN IF NOT EXISTS knowledge_point_id BIGINT')
    op.execute('ALTER TABLE tags ADD COLUMN IF NOT EXISTS sort_order BIGINT DEFAULT 0')
    op.execute('UPDATE tags SET sort_order = 0 WHERE sort_order IS NULL')
    op.execute('ALTER TABLE tags ALTER COLUMN sort_order SET NOT NULL')
    
    # 修改字段类型和注释
    op.execute('ALTER TABLE tags ALTER COLUMN name TYPE VARCHAR(200)')
    
    # 删除旧字段
    op.execute('ALTER TABLE tags DROP COLUMN IF EXISTS parent_id')
    op.execute('ALTER TABLE tags DROP COLUMN IF EXISTS level')
    
    # 修改索引
    op.execute('DROP INDEX IF EXISTS ix_tags_name')
    op.execute('CREATE INDEX IF NOT EXISTS ix_tags_name ON tags(name)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_tags_knowledge_point_id ON tags(knowledge_point_id)')
    
    # 添加新的外键约束
    op.execute('ALTER TABLE tags ADD CONSTRAINT tags_knowledge_point_id_fkey FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE')


def downgrade() -> None:
    """回滚操作"""
    raise NotImplementedError("This migration cannot be downgraded")

