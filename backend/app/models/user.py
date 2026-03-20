"""
用户模型
定义用户和管理员的数据库模型
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.user_question import UserQuestion

import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"      # 正常
    DISABLED = "disabled"  # 禁用
    DELETED = "deleted"    # 已删除


class Gender(str, Enum):
    """性别"""
    UNKNOWN = "unknown"
    MALE = "male"
    FEMALE = "female"


class User(Base):
    """用户表"""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="用户ID"
    )
    
    # 登录凭证
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, index=True, comment="手机号"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True, index=True, comment="邮箱"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希"
    )
    
    # 基本信息
    nickname: Mapped[str] = mapped_column(
        String(50), nullable=False, default="", comment="昵称"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="头像URL"
    )
    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender), default=Gender.UNKNOWN, comment="性别"
    )
    birthday: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="生日"
    )
    
    # 状态
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, comment="状态"
    )

    disabled_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="禁用原因"
    )
    disabled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="禁用时间"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )
    
    # 关系
    user_questions: Mapped[list["UserQuestion"]] = relationship(
        "UserQuestion", back_populates="user"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone={self.phone}, email={self.email})>"


class Admin(Base):
    """管理员表"""
    
    __tablename__ = "admins"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="管理员ID"
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="用户名"
    )
    
    # 登录凭证（手机号或邮箱至少一个）
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, index=True, comment="手机号"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True, index=True, comment="邮箱"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希"
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, default="", comment="姓名"
    )
    
    # 状态
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否启用"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )
    
    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, phone={self.phone}, email={self.email})>"

