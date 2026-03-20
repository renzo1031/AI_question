"""系统配置模型"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemConfig(Base):
    """系统配置表 - 存储邮件、短信等系统配置"""
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="配置ID"
    )

    config_key: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, comment="配置键（唯一）"
    )
    config_group: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="配置分组（email/sms/system等）"
    )
    config_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="配置名称"
    )
    config_value: Mapped[str] = mapped_column(
        Text, nullable=False, comment="配置值（敏感信息需加密）"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="配置说明"
    )
    
    is_encrypted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否加密存储"
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用"
    )

    # 元数据
    created_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="创建管理员ID"
    )
    updated_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="更新管理员ID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.config_key}, group={self.config_group})>"
