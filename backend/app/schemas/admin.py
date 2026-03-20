"""
管理员Schema
定义管理员相关的请求和响应数据模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.common.utils import is_valid_email, is_valid_phone


# ==================== 注册相关 ====================

class AdminRegisterByPhoneRequest(BaseModel):
    """手机号注册管理员请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    verify_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v


class AdminRegisterByEmailRequest(BaseModel):
    """邮箱注册管理员请求"""
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    verify_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not is_valid_email(v):
            raise ValueError("邮箱格式不正确")
        return v


# ==================== 登录相关 ====================

class AdminLoginByPasswordRequest(BaseModel):
    """管理员密码登录请求"""
    account: str = Field(..., description="手机号或邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")


class AdminLoginByVerifyCodeRequest(BaseModel):
    """管理员验证码登录请求"""
    account: str = Field(..., description="手机号或邮箱")
    verify_code: str = Field(..., min_length=4, max_length=6, description="验证码")


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""


# ==================== 管理员信息 ====================

class AdminInfoResponse(BaseModel):
    """管理员信息响应"""
    id: str = Field(..., description="管理员ID")
    name: str = Field(..., description="姓名")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True


class ResetUserPasswordRequest(BaseModel):
    """管理员重置用户密码请求"""
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")


class UpdateAdminInfoRequest(BaseModel):
    """更新管理员信息请求"""
    name: Optional[str] = Field(None, max_length=50, description="姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_email(v):
            raise ValueError("邮箱格式不正确")
        return v


class ChangeAdminPasswordRequest(BaseModel):
    """修改管理员密码请求"""
    old_password: str = Field(..., min_length=6, max_length=32, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str, info) -> str:
        old_password = info.data.get("old_password")
        if v == old_password:
            raise ValueError("新密码不能与旧密码相同")
        return v


# ==================== 管理员管理 ====================

class CreateAdminRequest(BaseModel):
    """创建管理员请求"""
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_email(v):
            raise ValueError("邮箱格式不正确")
        return v
    
    @model_validator(mode="after")
    def validate_at_least_one(self):
        """至少填写手机号或邮箱一个"""
        if not self.phone and not self.email:
            raise ValueError("手机号和邮箱至少填写一个")
        return self


class AdminListQuery(BaseModel):
    """管理员列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, max_length=50, description="搜索关键词（手机号/邮箱/姓名）")
    is_active: Optional[bool] = Field(None, description="状态筛选")


class UpdateAdminRequest(BaseModel):
    """更新管理员请求"""
    name: Optional[str] = Field(None, max_length=50, description="姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    is_active: Optional[bool] = Field(None, description="是否启用")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_phone(v):
            raise ValueError("手机号格式不正确")
        return v
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_valid_email(v):
            raise ValueError("邮箱格式不正确")
        return v


class ResetAdminPasswordRequest(BaseModel):
    """重置管理员密码请求"""
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")


# ==================== 用户管理（管理员使用） ====================

class UserListQuery(BaseModel):
    """用户列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, max_length=50, description="搜索关键词（手机号/邮箱/昵称）")
    status: Optional[str] = Field(None, description="状态筛选")
    created_from: Optional[datetime] = Field(None, description="注册时间开始（上海时区）")
    created_to: Optional[datetime] = Field(None, description="注册时间结束（上海时区）")
    last_login_from: Optional[datetime] = Field(None, description="最后登录开始（上海时区）")
    last_login_to: Optional[datetime] = Field(None, description="最后登录结束（上海时区）")


class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求"""
    status: str = Field(..., description="状态：active/disabled")
    disabled_reason: Optional[str] = Field(None, max_length=500, description="禁用原因（仅当 status=disabled 时可填）")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("active", "disabled"):
            raise ValueError("状态只能是 active 或 disabled")
        return v


class UserDetailResponse(BaseModel):
    """用户详情响应（管理员查看）"""
    id: str = Field(..., description="用户ID")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    nickname: str = Field(..., description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: str = Field(..., description="性别")
    birthday: Optional[datetime] = Field(None, description="生日")
    status: str = Field(..., description="状态")
    disabled_reason: Optional[str] = Field(None, description="禁用原因")
    disabled_at: Optional[datetime] = Field(None, description="禁用时间")
    created_at: datetime = Field(..., description="注册时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True
