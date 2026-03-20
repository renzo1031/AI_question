"""
数据库连接模块
提供异步PostgreSQL数据库连接
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 开发环境打印SQL
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 连接池预检
)

# 创建异步Session工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy ORM基类"""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    用于FastAPI依赖注入
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话上下文管理器
    用于非依赖注入场景
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库，创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()

