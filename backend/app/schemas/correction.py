"""
题目纠错相关的 Pydantic Schema
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionCorrectionCreateSchema(BaseModel):
    """用户提交纠错的请求 Schema"""
    question_id: int = Field(..., description="题目ID")
    reason: Optional[str] = Field(None, max_length=1000, description="纠错原因/描述")


class QuestionCorrectionUpdateSchema(BaseModel):
    """管理员更新纠错状态的请求 Schema"""
    status: str = Field(..., pattern="^(resolved|ignored)$", description="状态：resolved(已解决)/ignored(已忽略)")
    admin_note: Optional[str] = Field(None, max_length=1000, description="管理员备注")


class QuestionCorrectionResponseSchema(BaseModel):
    """纠错记录响应 Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    question_id: int
    user_id: Optional[str]
    reason: Optional[str]
    status: str
    admin_note: Optional[str]
    handled_by: Optional[str]
    handled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    @field_validator('user_id', 'handled_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, value):
        """将 UUID 对象转换为字符串"""
        if value is None:
            return None
        if isinstance(value, UUID):
            return str(value)
        return value


class QuestionCorrectionListSchema(BaseModel):
    """纠错记录列表响应 Schema"""
    items: list[QuestionCorrectionResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class QuestionCorrectionQuerySchema(BaseModel):
    """纠错记录查询参数 Schema"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    status: Optional[str] = Field(None, pattern="^(pending|resolved|ignored)$", description="状态筛选")
    question_id: Optional[int] = Field(None, description="题目ID筛选")
