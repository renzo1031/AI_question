"""add system_configs table

Revision ID: 0008_system_configs
Revises: 0007_repair_kp_subject_id
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008_system_configs"
down_revision: Union[str, None] = "0006_add_subjects"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_configs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="配置ID"),
        sa.Column("config_key", sa.String(length=100), nullable=False, comment="配置键（唯一）"),
        sa.Column("config_group", sa.String(length=50), nullable=False, comment="配置分组（email/sms/system等）"),
        sa.Column("config_name", sa.String(length=200), nullable=False, comment="配置名称"),
        sa.Column("config_value", sa.Text(), nullable=False, comment="配置值（敏感信息需加密）"),
        sa.Column("description", sa.Text(), nullable=True, comment="配置说明"),
        sa.Column("is_encrypted", sa.Boolean(), nullable=False, server_default="false", comment="是否加密存储"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true", comment="是否启用"),
        sa.Column("created_by_admin_id", postgresql.UUID(as_uuid=True), nullable=True, comment="创建管理员ID"),
        sa.Column("updated_by_admin_id", postgresql.UUID(as_uuid=True), nullable=True, comment="更新管理员ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_key", name="uq_system_config_key")
    )
    
    op.create_index("ix_system_configs_group", "system_configs", ["config_group"])
    op.create_index("ix_system_configs_key", "system_configs", ["config_key"])


def downgrade() -> None:
    op.drop_index("ix_system_configs_key", table_name="system_configs")
    op.drop_index("ix_system_configs_group", table_name="system_configs")
    op.drop_table("system_configs")
