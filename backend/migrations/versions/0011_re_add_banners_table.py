"""re-add banners table (without title column)

Revision ID: 0011_re_add_banners_table
Revises: 0010_merge_heads
Create Date: 2026-02-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_re_add_banners_table"
down_revision: Union[str, None] = "0010_merge_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "banners",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="轮播图ID"),
        sa.Column("image_url", sa.String(length=500), nullable=False, comment="MinIO 访问 URL"),
        sa.Column("image_key", sa.String(length=500), nullable=False, comment="MinIO 对象键（用于删除）"),
        sa.Column("link_url", sa.String(length=500), nullable=True, comment="点击跳转链接"),
        sa.Column(
            "link_type",
            sa.String(length=20),
            nullable=False,
            server_default="none",
            comment="链接类型：external / internal / none",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="是否启用",
        ),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True, comment="生效时间（可选）"),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True, comment="失效时间（可选）"),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="排序（值越大越靠前）",
        ),
        sa.Column(
            "created_by_admin_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="创建管理员ID",
        ),
        sa.Column(
            "updated_by_admin_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="更新管理员ID",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_banners_is_active", "banners", ["is_active"])
    op.create_index("ix_banners_sort_order", "banners", ["sort_order"])


def downgrade() -> None:
    op.drop_index("ix_banners_sort_order", table_name="banners")
    op.drop_index("ix_banners_is_active", table_name="banners")
    op.drop_table("banners")
