"""replace admin_logs and user_logs with unified operation_logs

Revision ID: 9aaaf810444d
Revises: 999cc7c8f711
Create Date: 2025-12-25 17:20:59.548728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9aaaf810444d'
down_revision: Union[str, None] = '999cc7c8f711'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 删除旧的 admin_logs 表
    op.drop_index('ix_admin_logs_admin_id', table_name='admin_logs', if_exists=True)
    op.drop_index('ix_admin_logs_created_at', table_name='admin_logs', if_exists=True)
    op.drop_index('ix_admin_logs_log_level', table_name='admin_logs', if_exists=True)
    op.drop_index('ix_admin_logs_module', table_name='admin_logs', if_exists=True)
    op.drop_table('admin_logs', if_exists=True)
    
    # 创建统一的 operation_logs 表
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True, comment='日志ID'),
        sa.Column('user_type', sa.String(length=20), nullable=False, comment='用户类型：admin/user'),
        sa.Column('user_id', postgresql.UUID(), nullable=True, comment='用户ID（管理员或普通用户）'),
        sa.Column('username', sa.String(length=100), nullable=True, comment='用户名（管理员用户名或用户手机号）'),
        sa.Column('log_level', sa.String(length=20), nullable=False, comment='日志级别'),
        sa.Column('module', sa.String(length=50), nullable=False, comment='所属模块'),
        sa.Column('action', sa.String(length=200), nullable=False, comment='操作动作'),
        sa.Column('description', sa.Text(), nullable=True, comment='操作描述'),
        sa.Column('request_method', sa.String(length=10), nullable=True, comment='HTTP请求方法'),
        sa.Column('request_path', sa.String(length=500), nullable=True, comment='请求路径'),
        sa.Column('request_params', postgresql.JSONB(), nullable=True, comment='请求参数'),
        sa.Column('ip_address', postgresql.INET(), nullable=True, comment='IP地址'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='User-Agent'),
        sa.Column('status_code', sa.Integer(), nullable=True, comment='HTTP状态码'),
        sa.Column('is_success', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='是否成功'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('response_time_ms', sa.Integer(), nullable=True, comment='响应时间(毫秒)'),
        sa.Column('extra_data', postgresql.JSONB(), nullable=True, comment='额外数据'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_operation_logs_user_type', 'operation_logs', ['user_type'])
    op.create_index('ix_operation_logs_user_id', 'operation_logs', ['user_id'])
    op.create_index('ix_operation_logs_log_level', 'operation_logs', ['log_level'])
    op.create_index('ix_operation_logs_module', 'operation_logs', ['module'])
    op.create_index('ix_operation_logs_created_at', 'operation_logs', ['created_at'])
    op.create_index('ix_operation_logs_user_type_user_id', 'operation_logs', ['user_type', 'user_id'])
    op.create_index('ix_operation_logs_user_type_created_at', 'operation_logs', ['user_type', 'created_at'])
    op.create_index('ix_operation_logs_module_created_at', 'operation_logs', ['module', 'created_at'])


def downgrade() -> None:
    # 删除 operation_logs 表
    op.drop_index('ix_operation_logs_module_created_at', table_name='operation_logs')
    op.drop_index('ix_operation_logs_user_type_created_at', table_name='operation_logs')
    op.drop_index('ix_operation_logs_user_type_user_id', table_name='operation_logs')
    op.drop_index('ix_operation_logs_created_at', table_name='operation_logs')
    op.drop_index('ix_operation_logs_module', table_name='operation_logs')
    op.drop_index('ix_operation_logs_log_level', table_name='operation_logs')
    op.drop_index('ix_operation_logs_user_id', table_name='operation_logs')
    op.drop_index('ix_operation_logs_user_type', table_name='operation_logs')
    op.drop_table('operation_logs')

