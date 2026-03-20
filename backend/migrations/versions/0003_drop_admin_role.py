"""drop admins.role

Revision ID: 0003_drop_admin_role
Revises: 0002_add_announcements
Create Date: 2025-12-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_drop_admin_role"
down_revision = "0002_add_announcements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) 删除 admins.role 列（若存在）
    if inspector.has_table("admins"):
        columns = {col["name"] for col in inspector.get_columns("admins")}
        if "role" in columns:
            op.drop_column("admins", "role")

    # 2) 尝试删除 Postgres enum type（若存在且未被引用）
    op.execute("DROP TYPE IF EXISTS adminrole")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("admins"):
        columns = {col["name"] for col in inspector.get_columns("admins")}
        if "role" not in columns:
            # 回滚：恢复 role 列（使用 VARCHAR，避免依赖 enum）
            op.add_column(
                "admins",
                sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'admin'")),
            )
