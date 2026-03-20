"""restructure_grades_and_knowledge_points

Revision ID: a6dac05e93c3
Revises: 0005_add_grade_knowledge_point
Create Date: 2025-12-24 18:42:47.453285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6dac05e93c3'
down_revision: Union[str, None] = '0005_add_grade_knowledge_point'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    重构年级和知识点表结构
    1. 删除旧的依赖表
    2. 重构 grades 和 knowledge_points 表
    """
    # 删除旧的外键约束和依赖表
    op.execute('DROP TABLE IF EXISTS question_knowledge CASCADE')
    op.execute('DROP TABLE IF EXISTS learning_profiles CASCADE')
    op.execute('DROP TABLE IF EXISTS feature_flags CASCADE')
    op.execute('DROP TABLE IF EXISTS chapters CASCADE')
    op.execute('DROP TABLE IF EXISTS subjects CASCADE')
    
    # 重构 grades 表
    op.execute('ALTER TABLE grades DROP CONSTRAINT IF EXISTS grades_subject_id_fkey')
    op.execute('ALTER TABLE grades DROP CONSTRAINT IF EXISTS uq_grade_subject_code')
    op.execute('ALTER TABLE grades DROP CONSTRAINT IF EXISTS uq_grade_subject_name')
    op.execute('ALTER TABLE grades DROP COLUMN IF EXISTS subject_id')
    op.execute('ALTER TABLE grades DROP COLUMN IF EXISTS code')
    op.execute('ALTER TABLE grades DROP COLUMN IF EXISTS created_at')
    op.execute('ALTER TABLE grades DROP COLUMN IF EXISTS updated_at')
    op.execute('ALTER TABLE grades ADD COLUMN IF NOT EXISTS sort_order BIGINT DEFAULT 0')
    op.execute('UPDATE grades SET sort_order = 0 WHERE sort_order IS NULL')
    op.execute('ALTER TABLE grades ALTER COLUMN sort_order SET NOT NULL')
    op.execute('ALTER TABLE grades ALTER COLUMN name TYPE VARCHAR(50)')
    op.execute('ALTER TABLE grades ALTER COLUMN description TYPE TEXT')
    op.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_grades_name ON grades(name)')
    
    # 重构 knowledge_points 表
    op.execute('ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS knowledge_points_subject_id_fkey')
    op.execute('ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS knowledge_points_chapter_id_fkey')
    op.execute('ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS knowledge_points_grade_id_fkey')
    op.execute('ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS uq_knowledge_point_chapter_code')
    op.execute('ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS uq_knowledge_point_chapter_name')
    op.execute('ALTER TABLE knowledge_points DROP COLUMN IF EXISTS subject_id')
    op.execute('ALTER TABLE knowledge_points DROP COLUMN IF EXISTS chapter_id')
    op.execute('ALTER TABLE knowledge_points DROP COLUMN IF EXISTS code')
    op.execute('ALTER TABLE knowledge_points DROP COLUMN IF EXISTS created_at')
    op.execute('ALTER TABLE knowledge_points DROP COLUMN IF EXISTS updated_at')
    op.execute('ALTER TABLE knowledge_points ADD COLUMN IF NOT EXISTS sort_order BIGINT DEFAULT 0')
    op.execute('UPDATE knowledge_points SET sort_order = 0 WHERE sort_order IS NULL')
    op.execute('ALTER TABLE knowledge_points ALTER COLUMN sort_order SET NOT NULL')
    op.execute('ALTER TABLE knowledge_points ALTER COLUMN name TYPE VARCHAR(200)')
    op.execute('ALTER TABLE knowledge_points ALTER COLUMN description TYPE TEXT')
    op.execute('CREATE INDEX IF NOT EXISTS ix_knowledge_points_grade_id ON knowledge_points(grade_id)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_knowledge_points_name ON knowledge_points(name)')
    op.execute('ALTER TABLE knowledge_points ADD CONSTRAINT knowledge_points_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE')
    
    # 其他表的小调整
    op.execute('DROP INDEX IF EXISTS ix_announcements_is_active')
    op.execute('DROP INDEX IF EXISTS ix_announcements_sort_order')
    op.execute('ALTER TABLE admins DROP COLUMN IF EXISTS permissions')
    op.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_admins_email ON admins(email)')
    op.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_admins_phone ON admins(phone)')
    
    # 添加唯一约束（先检查是否存在）
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_question_tag'
            ) THEN
                ALTER TABLE question_tags ADD CONSTRAINT uq_question_tag UNIQUE (question_id, tag_id);
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_user_question'
            ) THEN
                ALTER TABLE user_questions ADD CONSTRAINT uq_user_question UNIQUE (user_id, question_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """回滚操作"""
    # 这个迁移不支持回滚，因为涉及删除表和数据
    raise NotImplementedError("This migration cannot be downgraded")

