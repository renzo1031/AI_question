"""change users and admins id to UUID

Revision ID: 0004_user_admin_uuid
Revises: 0003_drop_admin_role
Create Date: 2025-12-24

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "0004_user_admin_uuid"
down_revision = "0003_drop_admin_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    
    # 查询所有引用 users.id 的外键约束
    result = bind.execute(sa.text("""
        SELECT tc.constraint_name, tc.table_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'users'
            AND ccu.column_name = 'id'
    """))
    user_fks = [(row[0], row[1]) for row in result]
    
    # 查询所有引用 admins.id 的外键约束
    result = bind.execute(sa.text("""
        SELECT tc.constraint_name, tc.table_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'admins'
            AND ccu.column_name = 'id'
    """))
    admin_fks = [(row[0], row[1]) for row in result]
    
    # 0) 清空相关表数据（开发环境，避免外键冲突）
    op.execute("TRUNCATE TABLE user_questions CASCADE")
    op.execute("TRUNCATE TABLE learning_profiles CASCADE")
    op.execute("TRUNCATE TABLE users CASCADE")
    op.execute("TRUNCATE TABLE admins CASCADE")
    op.execute("TRUNCATE TABLE announcements CASCADE")
    
    # 1) 删除所有引用 users.id 的外键约束
    for fk_name, table_name in user_fks:
        op.drop_constraint(fk_name, table_name, type_="foreignkey")
    
    # 2) 修改 users.id 列类型为 UUID
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE UUID USING gen_random_uuid()")
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT gen_random_uuid()")
    
    # 3) 修改所有引用 users.id 的外键列类型
    op.execute("ALTER TABLE user_questions ALTER COLUMN user_id TYPE UUID USING gen_random_uuid()")
    op.execute("ALTER TABLE learning_profiles ALTER COLUMN user_id TYPE UUID USING gen_random_uuid()")
    
    # 4) 重建外键约束
    for fk_name, table_name in user_fks:
        op.create_foreign_key(
            fk_name,
            table_name,
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE"
        )
    
    # 5) 删除所有引用 admins.id 的外键约束
    for fk_name, table_name in admin_fks:
        op.drop_constraint(fk_name, table_name, type_="foreignkey")
    
    # 6) 修改 admins.id 列类型为 UUID
    op.execute("ALTER TABLE admins ALTER COLUMN id DROP DEFAULT")
    op.execute("ALTER TABLE admins ALTER COLUMN id TYPE UUID USING gen_random_uuid()")
    op.execute("ALTER TABLE admins ALTER COLUMN id SET DEFAULT gen_random_uuid()")
    
    # 7) 修改 announcements 表的管理员 ID 外键列类型
    op.execute("ALTER TABLE announcements ALTER COLUMN created_by_admin_id TYPE UUID USING NULL")
    op.execute("ALTER TABLE announcements ALTER COLUMN updated_by_admin_id TYPE UUID USING NULL")


def downgrade() -> None:
    # 回滚：将 UUID 改回 INTEGER（会丢失数据）
    
    # 1) 回滚 admins 表
    op.execute("ALTER TABLE announcements ALTER COLUMN created_by_admin_id TYPE INTEGER USING NULL")
    op.execute("ALTER TABLE announcements ALTER COLUMN updated_by_admin_id TYPE INTEGER USING NULL")
    
    op.execute("ALTER TABLE admins ALTER COLUMN id DROP DEFAULT")
    op.execute("ALTER TABLE admins ALTER COLUMN id TYPE INTEGER USING 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS admins_id_seq")
    op.execute("ALTER TABLE admins ALTER COLUMN id SET DEFAULT nextval('admins_id_seq')")
    
    # 2) 回滚 users 表
    op.drop_constraint("user_questions_user_id_fkey", "user_questions", type_="foreignkey")
    
    op.execute("ALTER TABLE user_questions ALTER COLUMN user_id TYPE INTEGER USING 1")
    
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE INTEGER USING 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq")
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")
    
    op.create_foreign_key(
        "user_questions_user_id_fkey",
        "user_questions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )
