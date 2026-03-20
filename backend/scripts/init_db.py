"""
数据库初始化脚本
创建初始管理员账户
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_factory, init_db
from app.core.security.password import password_handler
from app.models.user import Admin


async def create_initial_admin():
    """创建初始管理员"""
    async with async_session_factory() as session:
        # 检查是否已存在管理员
        from sqlalchemy import select
        result = await session.execute(select(Admin))
        if result.scalar_one_or_none():
            print("管理员已存在，跳过创建")
            return
        
        # 创建初始管理员（使用手机号）
        admin = Admin(
            phone="13800138000",
            password_hash=password_handler.hash("admin123"),
            name="初始管理员",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("初始管理员创建成功")
        print("手机号: 13800138000")
        print("密码: admin123")
        print("请登录后立即修改密码！")


async def main():
    """主函数"""
    print("正在初始化数据库...")
    await init_db()
    print("数据库表创建成功")
    
    print("\n正在创建初始管理员...")
    await create_initial_admin()
    
    print("\n数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())

