"""
认证中间件
提供JWT和Session认证依赖
"""
from typing import Optional

from fastapi import Cookie, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AuthException, ErrorCode
from app.core.database import get_db
from app.core.redis import redis_client
from app.core.security.jwt import jwt_handler
from app.core.security.session import session_manager


async def get_current_user_id(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    获取当前登录用户ID（JWT认证）
    
    用于普通用户API
    """
    if not authorization:
        raise AuthException(
            code=ErrorCode.UNAUTHORIZED,
            message="请先登录"
        )
    
    # 提取Token
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token格式错误"
        )
    
    # 检查Token是否在黑名单
    if await redis_client.is_token_blacklisted(token):
        raise AuthException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token已失效"
        )
    
    # 验证Token
    payload = jwt_handler.verify_access_token(token)
    if not payload:
        raise AuthException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token无效或已过期"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token数据无效"
        )
    
    return str(user_id)


async def get_current_user_id_optional(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[str]:
    """
    获取当前登录用户ID（可选）
    
    用于可登录可不登录的API
    """
    from loguru import logger
    
    if not authorization:
        logger.debug("没有 Authorization header")
        return None
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        logger.debug(f"Token 格式错误: scheme={scheme}, token={是否有token: {bool(token)}}")
        return None
    
    if await redis_client.is_token_blacklisted(token):
        logger.debug("Token 在黑名单中")
        return None
    
    payload = jwt_handler.verify_access_token(token)
    if not payload:
        logger.debug("Token 验证失败")
        return None
    
    user_id = payload.get("sub")
    logger.debug(f"Token payload: {payload}, user_id: {user_id}")
    if user_id:
        return str(user_id)
    return None


async def get_current_admin_id(
    session_id: Optional[str] = Cookie(None, alias="admin_session")
) -> str:
    """
    获取当前登录管理员ID（Session认证）
    
    用于管理后台API
    """
    if not session_id:
        raise AuthException(
            code=ErrorCode.SESSION_INVALID,
            message="请先登录管理后台"
        )
    
    admin_id = await session_manager.get_admin_id(session_id)
    if not admin_id:
        raise AuthException(
            code=ErrorCode.SESSION_EXPIRED,
            message="登录已过期，请重新登录"
        )
    
    # 刷新Session
    await session_manager.refresh_session(session_id)
    
    return admin_id


async def get_current_admin_id_optional(
    session_id: Optional[str] = Cookie(None, alias="admin_session")
) -> Optional[str]:
    """
    获取当前登录管理员ID（可选）
    """
    if not session_id:
        return None
    
    admin_id = await session_manager.get_admin_id(session_id)
    if admin_id:
        await session_manager.refresh_session(session_id)
    return admin_id

