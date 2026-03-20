"""
用户信息管理API路由
提供用户信息查询、更新、密码修改、绑定手机/邮箱等接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.middleware.auth import get_current_user_id
from app.schemas.user import (
    BindEmailRequest,
    BindPhoneRequest,
    ChangePasswordRequest,
    UpdateUserInfoRequest,
)
from app.services.user import UserService

router = APIRouter(prefix="/user", tags=["用户"])


# ==================== 用户信息 ====================

@router.get("/info", summary="获取用户信息", dependencies=[Depends(jwt_security)])
async def get_user_info(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前登录用户信息
    
    需要JWT Token认证
    """
    service = UserService(db)
    user_info = await service.get_user_info(user_id)
    return success(data=user_info.model_dump(mode="json"))


@router.put("/info", summary="更新用户信息", dependencies=[Depends(jwt_security)])
async def update_user_info(
    request: UpdateUserInfoRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前登录用户信息
    
    - **nickname**: 昵称
    - **avatar**: 头像URL
    - **gender**: 性别
    - **birthday**: 生日
    
    需要JWT Token认证
    """
    service = UserService(db)
    user_info = await service.update_user_info(
        user_id=user_id,
        nickname=request.nickname,
        avatar=request.avatar,
        gender=request.gender,
        birthday=request.birthday
    )
    return success(data=user_info.model_dump(mode="json"), message="更新成功")


# ==================== 密码管理 ====================

@router.post("/password/change", summary="修改密码", dependencies=[Depends(jwt_security)])
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码
    
    需要JWT Token认证
    """
    service = UserService(db)
    await service.change_password(
        user_id=user_id,
        old_password=request.old_password,
        new_password=request.new_password
    )
    return success(message="密码修改成功")


# ==================== 绑定手机/邮箱 ====================

@router.post("/bind/phone", summary="绑定手机号", dependencies=[Depends(jwt_security)])
async def bind_phone(
    request: BindPhoneRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    绑定或更换手机号
    
    - **phone**: 手机号
    - **verify_code**: 验证码
    
    需要JWT Token认证
    """
    service = UserService(db)
    await service.bind_phone(
        user_id=user_id,
        phone=request.phone,
        verify_code=request.verify_code
    )
    return success(message="手机号绑定成功")


@router.post("/bind/email", summary="绑定邮箱", dependencies=[Depends(jwt_security)])
async def bind_email(
    request: BindEmailRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    绑定或更换邮箱
    
    - **email**: 邮箱地址
    - **verify_code**: 验证码
    
    需要JWT Token认证
    """
    service = UserService(db)
    await service.bind_email(
        user_id=user_id,
        email=request.email,
        verify_code=request.verify_code
    )
    return success(message="邮箱绑定成功")
