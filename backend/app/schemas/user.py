"""
用户Schema
定义用户相关的请求和响应数据模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.common.utils import is_valid_phone
from app.models.user import Gender, UserStatus


# ==================== 验证码相关 ====================

class SendVerifyCodeRequest(BaseModel):
    """发送验证码请求"""
    target: str = Field(..., description="手机号或邮箱")
    scene: str = Field(
        default="register", 
        description="场景：register-注册, login-登录, reset_password-重置密码"
    )
    
    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("请输入手机号或邮箱")
        return v


# ==================== 注册相关 ====================

class RegisterByPhoneRequest(BaseModel):
    """手机号注册请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v


class RegisterByEmailRequest(BaseModel):
    """邮箱注册请求"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


# ==================== 登录相关 ====================

class LoginByPasswordRequest(BaseModel):
    """密码登录请求"""
    account: str = Field(..., description="手机号或邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")


class LoginByVerifyCodeRequest(BaseModel):
    """验证码登录请求"""
    target: str = Field(..., description="手机号或邮箱")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")


class LoginResponse(BaseModel):
    """登录响应"""
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(..., description="访问Token")
    refresh_token: str = Field(..., description="刷新Token")
    token_type: str = Field(default="Bearer", description="Token类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    access_expire_at: int = Field(
        ...,
        alias="accessExpireAt",
        serialization_alias="accessExpireAt",
        description="访问Token过期时间戳（毫秒）"
    )


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str = Field(..., description="刷新Token")


# ==================== 用户信息 ====================

class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: str = Field(..., description="用户ID")
    phone: Optional[str] = Field(None, description="手机号（脱敏）")
    email: Optional[str] = Field(None, description="邮箱（脱敏）")
    nickname: str = Field(..., description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: Gender = Field(..., description="性别")
    birthday: Optional[datetime] = Field(None, description="生日")
    status: UserStatus = Field(..., description="状态")
    created_at: datetime = Field(..., description="注册时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    gender: Optional[Gender] = Field(None, description="性别")
    birthday: Optional[datetime] = Field(None, description="生日")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=32, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str, info) -> str:
        old_password = info.data.get("old_password")
        if v == old_password:
            raise ValueError("新密码不能与旧密码相同")
        return v


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    target: str = Field(..., description="手机号或邮箱")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")


class BindPhoneRequest(BaseModel):
    """绑定手机号请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v


class BindEmailRequest(BaseModel):
    """绑定邮箱请求"""
    email: EmailStr = Field(..., description="邮箱")
    verify_code: str = Field(..., min_length=4, max_length=8, description="验证码")

