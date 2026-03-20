"""
管理员API路由
提供管理员注册、登录、管理员管理、用户管理等接口
"""
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.admin import (
    AdminLoginByPasswordRequest,
    AdminLoginByVerifyCodeRequest,
    AdminRegisterByEmailRequest,
    AdminRegisterByPhoneRequest,
    ChangeAdminPasswordRequest,
    ResetUserPasswordRequest,
    UpdateAdminInfoRequest,
    UpdateUserStatusRequest,
)
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["管理员"])


# ==================== 注册 ====================

@router.post("/register/phone", summary="手机号注册管理员")
async def admin_register_by_phone(
    request: AdminRegisterByPhoneRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号注册管理员
    
    - **phone**: 手机号
    - **password**: 密码
    - **username**: 用户名
    - **verify_code**: 验证码
    """
    service = AdminService(db)
    admin = await service.register_by_phone(
        phone=request.phone,
        password=request.password,
        username=request.username,
        verify_code=request.verify_code
    )
    return success(message="注册成功", data={"admin_id": admin.id})


@router.post("/register/email", summary="邮箱注册管理员")
async def admin_register_by_email(
    request: AdminRegisterByEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    邮箱注册管理员
    
    - **email**: 邮箱
    - **password**: 密码
    - **username**: 用户名
    - **verify_code**: 验证码
    """
    service = AdminService(db)
    admin = await service.register_by_email(
        email=request.email,
        password=request.password,
        username=request.username,
        verify_code=request.verify_code
    )
    return success(message="注册成功", data={"admin_id": admin.id})


# ==================== 登录登出 ====================

@router.post("/login/password", summary="管理员密码登录")
async def admin_login_by_password(
    request: AdminLoginByPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    管理员密码登录
    
    登录成功后会设置Session Cookie
    
    - **account**: 手机号或邮箱
    - **password**: 密码
    """
    service = AdminService(db)
    session_cookie = await service.login_by_password(
        account=request.account,
        password=request.password
    )
    
    # 创建响应并设置Cookie
    response = JSONResponse(
        content=success(message="登录成功")
    )
    response.set_cookie(
        key="admin_session",
        value=session_cookie,
        httponly=True,
        max_age=86400,  # 24小时
        samesite="lax"
    )
    
    return response


@router.post("/login/verify-code", summary="管理员验证码登录")
async def admin_login_by_verify_code(
    request: AdminLoginByVerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    管理员验证码登录
    
    登录成功后会设置Session Cookie
    
    - **account**: 手机号或邮箱
    - **verify_code**: 验证码
    """
    service = AdminService(db)
    session_cookie = await service.login_by_verify_code(
        account=request.account,
        verify_code=request.verify_code
    )
    
    # 创建响应并设置Cookie
    response = JSONResponse(
        content=success(message="登录成功")
    )
    response.set_cookie(
        key="admin_session",
        value=session_cookie,
        httponly=True,
        max_age=86400,  # 24小时
        samesite="lax"
    )
    
    return response


@router.post("/logout", summary="管理员登出", dependencies=[Depends(session_security)])
async def admin_logout(
    session_id: Optional[str] = Cookie(None, alias="admin_session"),
    db: AsyncSession = Depends(get_db)
):
    """
    管理员登出
    
    清除Session Cookie
    """
    if session_id:
        service = AdminService(db)
        await service.logout(session_id)
    
    response = JSONResponse(content=success(message="已退出登录"))
    response.delete_cookie(key="admin_session")
    
    return response


# ==================== 当前管理员 ====================

@router.get("/me", summary="获取当前管理员信息", dependencies=[Depends(session_security)])
async def get_current_admin_info(
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前登录的管理员信息
    """
    service = AdminService(db)
    admin_info = await service.get_current_admin(admin_id)
    return success(data=admin_info.model_dump(mode="json"))


@router.put("/me", summary="更新当前管理员信息", dependencies=[Depends(session_security)])
async def update_current_admin_info(
    request: UpdateAdminInfoRequest,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前登录的管理员信息
    
    - **name**: 姓名
    - **phone**: 手机号
    - **email**: 邮箱
    """
    service = AdminService(db)
    admin_info = await service.update_current_admin(
        admin_id=admin_id,
        name=request.name,
        phone=request.phone,
        email=request.email
    )
    return success(data=admin_info.model_dump(mode="json"), message="更新成功")


@router.post("/me/password", summary="修改当前管理员密码", dependencies=[Depends(session_security)])
async def change_admin_password(
    request: ChangeAdminPasswordRequest,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    修改当前管理员密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    service = AdminService(db)
    await service.change_password(
        admin_id=admin_id,
        old_password=request.old_password,
        new_password=request.new_password
    )
    return success(message="密码修改成功")


# ==================== 用户管理（管理员使用） ====================

@router.get("/users/list", summary="获取用户列表", dependencies=[Depends(session_security)])
async def get_user_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(default=None, max_length=50, description="搜索关键词"),
    status: Optional[str] = Query(default=None, description="状态筛选"),
    created_from: Optional[str] = Query(default=None, description="注册时间开始（ISO8601）"),
    created_to: Optional[str] = Query(default=None, description="注册时间结束（ISO8601）"),
    last_login_from: Optional[str] = Query(default=None, description="最后登录开始（ISO8601）"),
    last_login_to: Optional[str] = Query(default=None, description="最后登录结束（ISO8601）"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **keyword**: 搜索关键词（手机号/邮箱/昵称）
    - **status**: 状态筛选（active/disabled）
    """
    from datetime import datetime

    def parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    service = AdminService(db)
    users, total = await service.get_user_list(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        created_from=parse_dt(created_from),
        created_to=parse_dt(created_to),
        last_login_from=parse_dt(last_login_from),
        last_login_to=parse_dt(last_login_to),
    )
    return page_success(
        data=[user.model_dump(mode="json") for user in users],
        page=page,
        page_size=page_size,
        total=total
    )


@router.get("/users/{user_id}", summary="获取用户详情", dependencies=[Depends(session_security)])
async def get_user_detail(
    user_id: str,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户详情
    """
    service = AdminService(db)
    user_detail = await service.get_user_detail(user_id)
    return success(data=user_detail.model_dump(mode="json"))


@router.put("/users/{user_id}/status", summary="更新用户状态", dependencies=[Depends(session_security)])
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户状态（启用/禁用）
    
    - **status**: 状态（active/disabled）
    """
    service = AdminService(db)
    user_detail = await service.update_user_status_with_reason(
        user_id=user_id,
        status=request.status,
        disabled_reason=request.disabled_reason
    )
    return success(data=user_detail.model_dump(mode="json"), message="状态更新成功")


@router.post(
    "/users/{user_id}/password",
    summary="管理员重置用户密码",
    dependencies=[Depends(session_security)]
)
async def reset_user_password(
    user_id: str,
    request: ResetUserPasswordRequest,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """管理员重置指定用户密码"""
    service = AdminService(db)
    await service.reset_user_password(user_id, request.new_password)
    return success(message="密码重置成功")


@router.get(
    "/users/{user_id}/learning-data",
    summary="获取用户学习数据（管理端）",
    dependencies=[Depends(session_security)]
)
async def get_user_learning_data(
    user_id: str,
    time_window_days: int = Query(default=30, ge=1, le=365, description="时间窗口（天数）"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db)
):
    """获取指定用户的学习概览、能力分析与进步反馈"""
    service = AdminService(db)
    data = await service.get_user_learning_data(user_id, time_window_days=time_window_days)
    return success(data=data)
