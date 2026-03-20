from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AnnouncementCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="公告标题")
    content: str = Field(..., min_length=1, description="公告内容")
    is_active: bool = Field(default=False, description="是否启用")
    start_at: Optional[datetime] = Field(default=None, description="生效时间")
    end_at: Optional[datetime] = Field(default=None, description="失效时间")
    sort_order: int = Field(default=0, description="排序（值越大越靠前）")


class AnnouncementUpdateSchema(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="公告标题")
    content: Optional[str] = Field(default=None, min_length=1, description="公告内容")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    start_at: Optional[datetime] = Field(default=None, description="生效时间")
    end_at: Optional[datetime] = Field(default=None, description="失效时间")
    sort_order: Optional[int] = Field(default=None, description="排序（值越大越靠前）")


class AnnouncementResponseSchema(BaseModel):
    id: int = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    content: str = Field(..., description="公告内容")
    is_active: bool = Field(..., description="是否启用")
    start_at: Optional[datetime] = Field(None, description="生效时间")
    end_at: Optional[datetime] = Field(None, description="失效时间")
    sort_order: int = Field(..., description="排序")
    created_by_admin_id: Optional[UUID] = Field(None, description="创建管理员ID")
    updated_by_admin_id: Optional[UUID] = Field(None, description="更新管理员ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('created_by_admin_id', 'updated_by_admin_id')
    def serialize_uuid(self, value: Optional[UUID]) -> Optional[str]:
        """将 UUID 对象序列化为字符串"""
        return str(value) if value else None


class AnnouncementPublicSchema(BaseModel):
    """用户端公告Schema（不包含管理员信息）"""
    id: int = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    content: str = Field(..., description="公告内容")
    start_at: Optional[datetime] = Field(None, description="生效时间")
    end_at: Optional[datetime] = Field(None, description="失效时间")
    sort_order: int = Field(..., description="排序")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(from_attributes=True)


class AnnouncementListQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(default=None, description="关键词搜索（标题/内容）")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
