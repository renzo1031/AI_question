"""轮播图模型
定义首页轮播图（管理端维护，图片存储于 MinIO）
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="轮播图ID"
    )
    image_url: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="MinIO 访问 URL"
    )
    image_key: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="MinIO 对象键（用于删除）"
    )
    link_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="点击跳转链接"
    )
    link_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="none", comment="链接类型：external / internal / none"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用"
    )
    start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="生效时间（可选）"
    )
    end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="失效时间（可选）"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="排序（值越大越靠前）"
    )
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
        return f"<Banner(id={self.id}, is_active={self.is_active})>"
