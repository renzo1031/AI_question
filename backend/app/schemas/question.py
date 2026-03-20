"""
搜题和题库相关Schema
定义搜题和题库相关的请求和响应数据模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# 导入年级/学科/知识点Schema
from app.schemas.grade_knowledge import (
    GradeResponseSchema,
    SubjectResponseSchema,
    KnowledgePointResponseSchema,
)


class SolveQuestionFromImageRequest(BaseModel):
    """从图片解题请求"""
    image_url: Optional[str] = Field(None, description="图片URL（与image_base64二选一）")
    image_base64: Optional[str] = Field(None, description="图片Base64编码（与image_url二选一）")
    ai_provider: Optional[str] = Field(None, description="AI提供商（tongyi/deepseek/kimi），不填使用默认")
    context: Optional[str] = Field(None, description="上下文信息（可选）")


class SolveQuestionFromTextRequest(BaseModel):
    """从文本解题请求"""
    question_text: str = Field(..., min_length=1, description="题目文本")
    ai_provider: Optional[str] = Field(None, description="AI提供商（tongyi/deepseek/kimi），不填使用默认")
    context: Optional[str] = Field(None, description="上下文信息（可选）")


class QuestionInfo(BaseModel):
    """题目信息"""
    content: str = Field(..., description="题目内容")
    grade: Optional[str] = Field(None, description="年级")
    knowledge_point: Optional[str] = Field(None, description="知识点")
    figure: Optional[list] = Field(None, description="配图位置信息")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")


class AnswerInfo(BaseModel):
    """答案信息"""
    content: str = Field(..., description="答案内容")
    provider: str = Field(..., description="AI提供商")
    model: str = Field(..., description="使用的模型")


class SolveQuestionResponse(BaseModel):
    """解题响应"""
    question: QuestionInfo = Field(..., description="题目信息")
    answer: AnswerInfo = Field(..., description="答案信息")


class AvailableProvidersResponse(BaseModel):
    """可用提供商列表响应"""
    providers: list[str] = Field(..., description="可用的AI提供商列表")


# ==================== 题库相关 ====================

class QuestionOptionSchema(BaseModel):
    """题目选项Schema"""
    id: int = Field(..., description="选项ID")
    option_key: str = Field(..., description="选项标识（如A、B、C、D）")
    option_text: str = Field(..., description="选项内容")
    
    model_config = ConfigDict(from_attributes=True)


class TagCreateSchema(BaseModel):
    """创建标签请求Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="标签名称")
    description: Optional[str] = Field(None, description="标签描述")
    parent_id: Optional[int] = Field(None, description="父标签ID")
    level: Optional[int] = Field(None, ge=1, le=20, description="标签层级")


class TagUpdateSchema(BaseModel):
    """更新标签请求Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="标签名称")
    description: Optional[str] = Field(None, description="标签描述")
    parent_id: Optional[int] = Field(None, description="父标签ID")
    level: Optional[int] = Field(None, ge=1, le=20, description="标签层级")


class QuestionOptionCreateSchema(BaseModel):
    """创建题目选项Schema"""
    option_key: str = Field(..., min_length=1, max_length=10, description="选项标识（如A、B、C、D）")
    option_text: str = Field(..., min_length=1, description="选项内容")


class TagSchema(BaseModel):
    """标签Schema"""
    id: int = Field(..., description="标签ID")
    name: str = Field(..., description="标签名称")
    description: Optional[str] = Field(None, description="标签描述")
    
    model_config = ConfigDict(from_attributes=True)


class QuestionCreateSchema(BaseModel):
    """创建题目请求Schema"""
    content: str = Field(..., min_length=1, description="题目内容")
    question_type: Optional[str] = Field(None, max_length=32, description="题目类型")
    difficulty: Optional[int] = Field(None, ge=1, le=10, description="难度等级（1-10）")
    source: Optional[str] = Field(None, max_length=32, description="来源")
    
    # 外键字段（优先使用）
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    subject_id: Optional[int] = Field(None, description="所属学科ID")
    knowledge_point_id: Optional[int] = Field(None, description="所属知识点ID")
    
    # 字符串字段（兼容旧代码）
    grade: Optional[str] = Field(None, max_length=50, description="年级（字符串，兼容）")
    subject: Optional[str] = Field(None, max_length=64, description="科目（字符串，兼容）")
    knowledge_point: Optional[str] = Field(None, max_length=200, description="知识点（字符串，兼容）")
    
    ai_answer: Optional[str] = Field(None, description="AI答案")
    ai_analysis: Optional[str] = Field(None, description="AI解析")
    options: Optional[list[QuestionOptionCreateSchema]] = Field(default_factory=list, description="题目选项列表")
    tag_ids: Optional[list[int]] = Field(default_factory=list, description="标签ID列表")


class QuestionUpdateSchema(BaseModel):
    """更新题目请求Schema（全量更新，字段可选）"""
    content: Optional[str] = Field(None, min_length=1, description="题目内容")
    question_type: Optional[str] = Field(None, max_length=32, description="题目类型")
    difficulty: Optional[int] = Field(None, ge=1, le=10, description="难度等级（1-10）")
    source: Optional[str] = Field(None, max_length=32, description="来源")
    
    # 外键字段
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    subject_id: Optional[int] = Field(None, description="所属学科ID")
    knowledge_point_id: Optional[int] = Field(None, description="所属知识点ID")
    
    # 字符串字段
    grade: Optional[str] = Field(None, max_length=50, description="年级（字符串，兼容）")
    subject: Optional[str] = Field(None, max_length=64, description="科目（字符串，兼容）")
    knowledge_point: Optional[str] = Field(None, max_length=200, description="知识点（字符串，兼容）")
    
    ai_answer: Optional[str] = Field(None, description="AI答案")
    ai_analysis: Optional[str] = Field(None, description="AI解析")
    options: Optional[list[QuestionOptionCreateSchema]] = Field(default_factory=list, description="题目选项列表")
    tag_ids: Optional[list[int]] = Field(default_factory=list, description="标签ID列表")


class QuestionImportRequestSchema(BaseModel):
    """批量导入题目请求Schema"""
    items: list[QuestionCreateSchema] = Field(..., description="题目列表")


class QuestionQuerySchema(BaseModel):
    """查询题目请求Schema"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    question_id: Optional[int] = Field(None, description="题目ID筛选")
    question_type: Optional[str] = Field(None, description="题目类型筛选")
    difficulty: Optional[int] = Field(None, ge=1, le=10, description="难度等级筛选")
    source: Optional[str] = Field(None, description="来源筛选")
    
    # 外键ID筛选
    grade_id: Optional[int] = Field(None, description="年级ID筛选")
    subject_id: Optional[int] = Field(None, description="学科ID筛选")
    knowledge_point_id: Optional[int] = Field(None, description="知识点ID筛选")
    
    # 字符串筛选（兼容）
    subject: Optional[str] = Field(None, description="科目筛选（字符串）")
    grade: Optional[str] = Field(None, description="年级筛选（字符串）")
    knowledge_point: Optional[str] = Field(None, description="知识点筛选（字符串）")
    
    tag_id: Optional[int] = Field(None, description="标签ID筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索（搜索题目内容）")


class QuestionResponseSchema(BaseModel):
    """题目响应Schema"""
    id: int = Field(..., description="题目ID")
    content: str = Field(..., description="题目内容")
    content_hash: str = Field(..., description="题目内容哈希")
    question_type: Optional[str] = Field(None, description="题目类型")
    difficulty: Optional[int] = Field(None, description="难度等级")
    source: Optional[str] = Field(None, description="来源")
    
    # 外键ID
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    subject_id: Optional[int] = Field(None, description="所属学科ID")
    knowledge_point_id: Optional[int] = Field(None, description="所属知识点ID")
    
    # 关联对象
    grade_obj: Optional[GradeResponseSchema] = Field(None, description="所属年级对象")
    subject_obj: Optional[SubjectResponseSchema] = Field(None, description="所属学科对象")
    knowledge_point_obj: Optional[KnowledgePointResponseSchema] = Field(None, description="所属知识点对象")
    
    # 字符串字段（兼容）
    grade: Optional[str] = Field(None, description="年级（兼容）")
    subject: Optional[str] = Field(None, description="科目（兼容）")
    knowledge_point: Optional[str] = Field(None, description="知识点（兼容）")
    
    ai_answer: Optional[str] = Field(None, description="AI答案")
    ai_analysis: Optional[str] = Field(None, description="AI解析")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    options: list[QuestionOptionSchema] = Field(default_factory=list, description="题目选项列表")
    tags: list[TagSchema] = Field(default_factory=list, description="标签列表")
    
    model_config = ConfigDict(from_attributes=True)


class QuestionListResponseSchema(BaseModel):
    """题目列表响应Schema"""
    items: list[QuestionResponseSchema] = Field(..., description="题目列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")

