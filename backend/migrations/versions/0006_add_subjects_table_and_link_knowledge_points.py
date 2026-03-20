"""add subjects table and link knowledge_points to subjects

Revision ID: 0006_add_subjects
Revises: a4762acc2863
Create Date: 2025-12-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_add_subjects"
down_revision: Union[str, None] = "a4762acc2863"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True, comment="学科ID"),
        sa.Column("name", sa.String(length=100), nullable=False, comment="学科名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="学科描述"),
        sa.Column("grade_id", sa.BigInteger(), nullable=False, comment="所属年级ID"),
        sa.Column("sort_order", sa.BigInteger(), nullable=False, server_default="0", comment="排序（值越小越靠前）"),
    )
    op.create_index("ix_subjects_grade_id", "subjects", ["grade_id"], unique=False)
    op.create_index("ix_subjects_name", "subjects", ["name"], unique=False)
    op.create_unique_constraint("uq_subjects_grade_id_name", "subjects", ["grade_id", "name"])
    op.create_foreign_key(
        "subjects_grade_id_fkey",
        "subjects",
        "grades",
        ["grade_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "knowledge_points",
        sa.Column("subject_id", sa.BigInteger(), nullable=True, comment="所属学科ID"),
    )
    op.create_index("ix_knowledge_points_subject_id", "knowledge_points", ["subject_id"], unique=False)

    op.execute(
        """
        INSERT INTO subjects (name, description, grade_id, sort_order)
        SELECT '默认', NULL, g.id, 0
        FROM grades g
        """
    )
    op.execute(
        """
        UPDATE knowledge_points kp
        SET subject_id = s.id
        FROM subjects s
        WHERE s.grade_id = kp.grade_id AND s.name = '默认'
        """
    )

    op.alter_column("knowledge_points", "subject_id", existing_type=sa.BigInteger(), nullable=False)
    op.create_foreign_key(
        "knowledge_points_subject_id_fkey",
        "knowledge_points",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute("ALTER TABLE knowledge_points DROP CONSTRAINT IF EXISTS knowledge_points_grade_id_fkey")
    op.drop_index("ix_knowledge_points_grade_id", table_name="knowledge_points")
    op.drop_column("knowledge_points", "grade_id")


def downgrade() -> None:
    raise NotImplementedError("This migration cannot be downgraded")

