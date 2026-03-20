"""
错题本相关Schema
定义错题本相关的请求和响应数据模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.practice import PracticeQuestionSchema


class WrongBookQuerySchema(BaseModel):
    """错题本查询请求Schema"""
    subject: Optional[str] = Field(None, description="学科筛选（如：数学、语文）")
    grade: Optional[str] = Field(None, description="年级筛选（如：七年级、八年级）")
    chapter: Optional[str] = Field(None, description="章节筛选（如：第一章、第二章）")
    knowledge_point: Optional[str] = Field(None, description="知识点筛选")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度等级筛选（1-5）")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class WrongBookItemSchema(BaseModel):
    """错题本项Schema"""
    question: PracticeQuestionSchema = Field(..., description="题目信息")
    wrong_count: int = Field(..., ge=0, description="错误次数")
    last_answer: Optional[str] = Field(None, description="最后一次答案")
    last_answer_at: Optional[datetime] = Field(None, description="最后一次答题时间")
    
    model_config = ConfigDict(from_attributes=True)

