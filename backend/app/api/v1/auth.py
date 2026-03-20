"""
用户认证API路由
提供注册、登录、登出、Token刷新等认证相关接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.schemas.user import (
    LoginByPasswordRequest,
    LoginByVerifyCodeRequest,
    RefreshTokenRequest,
    RegisterByEmailRequest,
    RegisterByPhoneRequest,
    ResetPasswordRequest,
    SendVerifyCodeRequest,
)
from app.services.user import UserService
from app.services.verify_code import verify_code_service

router = APIRouter(prefix="/auth", tags=["认证"])


# ==================== 验证码 ====================

@router.post("/verify-code/send", summary="发送验证码")
async def send_verify_code(request: SendVerifyCodeRequest):
    """
    发送验证码到手机或邮箱
    
    - **target**: 手机号或邮箱
    - **scene**: 场景类型 (register/login/reset_password/bind)
    """
    await verify_code_service.send_code(request.target, request.scene)
    return success(message="验证码已发送")


# ==================== 注册 ====================

@router.post("/register/phone", summary="手机号注册")
async def register_by_phone(
    request: RegisterByPhoneRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    使用手机号注册新用户
    
    - **phone**: 手机号
    - **password**: 密码（6-32位）
    - **verify_code**: 验证码
    - **nickname**: 昵称（可选）
    """
    service = UserService(db)
    user = await service.register_by_phone(
        phone=request.phone,
        password=request.password,
        verify_code=request.verify_code,
        nickname=request.nickname
    )
    return success(data={"user_id": user.id}, message="注册成功")


@router.post("/register/email", summary="邮箱注册")
async def register_by_email(
    request: RegisterByEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    使用邮箱注册新用户
    
    - **email**: 邮箱地址
    - **password**: 密码（6-32位）
    - **verify_code**: 验证码
    - **nickname**: 昵称（可选）
    """
    service = UserService(db)
    user = await service.register_by_email(
        email=request.email,
        password=request.password,
        verify_code=request.verify_code,
        nickname=request.nickname
    )
    return success(data={"user_id": user.id}, message="注册成功")


# ==================== 登录 ====================

@router.post("/login/password", summary="密码登录")
async def login_by_password(
    request: LoginByPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    使用密码登录
    
    - **account**: 手机号或邮箱
    - **password**: 密码
    """
    service = UserService(db)
    login_response = await service.login_by_password(
        account=request.account,
        password=request.password
    )
    return success(data=login_response.model_dump(mode="json", by_alias=True), message="登录成功")


@router.post("/login/verify-code", summary="验证码登录")
async def login_by_verify_code(
    request: LoginByVerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    使用验证码登录
    
    - **target**: 手机号或邮箱
    - **verify_code**: 验证码
    """
    service = UserService(db)
    login_response = await service.login_by_verify_code(
        target=request.target,
        verify_code=request.verify_code
    )
    return success(data=login_response.model_dump(mode="json", by_alias=True), message="登录成功")


# ==================== Token管理 ====================

@router.post("/token/refresh", summary="刷新Token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    使用RefreshToken获取新的AccessToken
    
    - **refresh_token**: 刷新Token
    """
    service = UserService(db)
    login_response = await service.refresh_token(request.refresh_token)
    return success(data=login_response.model_dump(mode="json", by_alias=True), message="Token刷新成功")


@router.post("/logout", summary="退出登录", dependencies=[Depends(jwt_security)])
async def logout(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    退出登录，将Token加入黑名单
    
    需要JWT Token认证
    """
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            service = UserService(db)
            await service.logout(token, refresh_token)
    
    return success(message="已退出登录")


# ==================== 密码重置 ====================

@router.post("/password/reset", summary="重置密码")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    通过验证码重置密码
    
    - **target**: 手机号或邮箱
    - **verify_code**: 验证码
    - **new_password**: 新密码
    """
    service = UserService(db)
    await service.reset_password(
        target=request.target,
        verify_code=request.verify_code,
        new_password=request.new_password
    )
    return success(message="密码重置成功")

