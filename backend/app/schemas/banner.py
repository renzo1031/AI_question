from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class BannerCreateSchema(BaseModel):
    image_url: str = Field(..., description="MinIO 访问 URL")
    image_key: str = Field(..., description="MinIO 对象键")
    link_url: Optional[str] = Field(default=None, max_length=500, description="点击跳转链接")
    link_type: Literal["external", "internal", "none"] = Field(default="none", description="链接类型")
    is_active: bool = Field(default=False, description="是否启用")
    start_at: Optional[datetime] = Field(default=None, description="生效时间")
    end_at: Optional[datetime] = Field(default=None, description="失效时间")
    sort_order: int = Field(default=0, description="排序（值越大越靠前）")


class BannerUpdateSchema(BaseModel):
    image_url: Optional[str] = Field(default=None, description="MinIO 访问 URL")
    image_key: Optional[str] = Field(default=None, description="MinIO 对象键")
    link_url: Optional[str] = Field(default=None, max_length=500, description="点击跳转链接")
    link_type: Optional[Literal["external", "internal", "none"]] = Field(default=None, description="链接类型")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    start_at: Optional[datetime] = Field(default=None, description="生效时间")
    end_at: Optional[datetime] = Field(default=None, description="失效时间")
    sort_order: Optional[int] = Field(default=None, description="排序（值越大越靠前）")


class BannerResponseSchema(BaseModel):
    id: int = Field(..., description="轮播图ID")
    image_url: str = Field(..., description="图片访问 URL")
    image_key: str = Field(..., description="MinIO 对象键")
    link_url: Optional[str] = Field(None, description="点击跳转链接")
    link_type: str = Field(..., description="链接类型")
    is_active: bool = Field(..., description="是否启用")
    start_at: Optional[datetime] = Field(None, description="生效时间")
    end_at: Optional[datetime] = Field(None, description="失效时间")
    sort_order: int = Field(..., description="排序")
    created_by_admin_id: Optional[UUID] = Field(None, description="创建管理员ID")
    updated_by_admin_id: Optional[UUID] = Field(None, description="更新管理员ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_by_admin_id", "updated_by_admin_id")
    def serialize_uuid(self, value: Optional[UUID]) -> Optional[str]:
        return str(value) if value else None


class BannerPublicSchema(BaseModel):
    """用户端轮播图 Schema（不含管理员信息）"""

    id: int = Field(..., description="轮播图ID")
    image_url: str = Field(..., description="图片访问 URL")
    link_url: Optional[str] = Field(None, description="点击跳转链接")
    link_type: str = Field(..., description="链接类型")
    sort_order: int = Field(..., description="排序")

    model_config = ConfigDict(from_attributes=True)


class BannerListQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class BannerUploadResponseSchema(BaseModel):
    image_url: str = Field(..., description="MinIO 公开访问 URL")
    image_key: str = Field(..., description="MinIO 对象键（创建时需要传入）")
