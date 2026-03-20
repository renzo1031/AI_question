"""公告模型
定义系统公告（管理端发布）
"""

from datetime import datetime
from typing import Optional

import uuid

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="公告ID"
    )

    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="公告标题"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="公告内容"
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
        return f"<Announcement(id={self.id}, title={self.title}, is_active={self.is_active})>"
