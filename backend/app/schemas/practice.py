"""
练习相关Schema
定义练习相关的请求和响应数据模型
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionOptionSchema


class PracticeGenerateSchema(BaseModel):
    """生成练习题请求Schema"""
    subject: str = Field(..., min_length=1, description="学科（如：数学、语文）")
    grade: Optional[str] = Field(None, description="年级（如：七年级、八年级）")
    chapter: Optional[str] = Field(None, description="章节（如：第一章、第二章）")
    knowledge_point: Optional[str] = Field(None, description="知识点")
    question_type: Optional[str] = Field(None, description="题目类型（如：选择题、填空题）")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度等级（1-5）")
    count: int = Field(default=10, ge=1, le=100, description="题目数量（默认10，最大100）")


class PracticeQuestionSchema(BaseModel):
    """练习题Schema"""
    id: int = Field(..., description="题目ID")
    content: str = Field(..., description="题目内容")
    question_type: str = Field(..., description="题目类型")
    difficulty: int = Field(..., description="难度等级")
    options: list[QuestionOptionSchema] = Field(default_factory=list, description="选项列表")
    tags: list[str] = Field(default_factory=list, description="标签名称列表（年级/章节/知识点）")
    
    model_config = ConfigDict(from_attributes=True)


class PracticeAnswerSchema(BaseModel):
    """练习答案提交Schema"""
    answer: str = Field(..., min_length=1, description="用户答案")


class PracticeCheckResultSchema(BaseModel):
    """练习答案校验结果Schema"""
    question_id: int = Field(..., description="题目ID")
    is_correct: bool = Field(..., description="答案是否正确")
    correct_answer: str = Field(..., description="正确答案")
    analysis: str = Field(..., description="解析")

