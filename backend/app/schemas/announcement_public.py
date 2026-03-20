from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AnnouncementPublicSchema(BaseModel):
    id: int = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    content: str = Field(..., description="公告内容")
    start_at: Optional[datetime] = Field(None, description="生效时间")
    end_at: Optional[datetime] = Field(None, description="失效时间")
    sort_order: int = Field(..., description="排序")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)
