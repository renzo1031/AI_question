"""add announcements

Revision ID: 0002_add_announcements
Revises: 0001_add_user_disabled_fields
Create Date: 2025-12-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_announcements"
down_revision = "0001_add_user_disabled_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("announcements"):
        op.create_table(
            "announcements",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True, comment="公告ID"),
            sa.Column("title", sa.String(length=200), nullable=False, comment="公告标题"),
            sa.Column("content", sa.Text(), nullable=False, comment="公告内容"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false"), comment="是否启用"),
            sa.Column("start_at", sa.DateTime(timezone=True), nullable=True, comment="生效时间（可选）"),
            sa.Column("end_at", sa.DateTime(timezone=True), nullable=True, comment="失效时间（可选）"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0"), comment="排序（值越大越靠前）"),
            sa.Column("created_by_admin_id", sa.Integer(), nullable=True, comment="创建管理员ID"),
            sa.Column("updated_by_admin_id", sa.Integer(), nullable=True, comment="更新管理员ID"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        )

    # 索引用 IF NOT EXISTS 保证幂等
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_announcements_is_active ON announcements (is_active)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_announcements_sort_order ON announcements (sort_order)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("announcements"):
        op.drop_index("ix_announcements_sort_order", table_name="announcements")
        op.drop_index("ix_announcements_is_active", table_name="announcements")
        op.drop_table("announcements")
