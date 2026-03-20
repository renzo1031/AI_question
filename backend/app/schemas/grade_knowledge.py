"""
年级、学科、知识点 Schema
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==================== 年级 Schema ====================

class GradeCreateSchema(BaseModel):
    """创建年级请求"""
    name: str = Field(..., min_length=1, max_length=50, description="年级名称")
    description: Optional[str] = Field(None, description="年级描述")
    sort_order: int = Field(default=0, description="排序")


class GradeUpdateSchema(BaseModel):
    """更新年级请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="年级名称")
    description: Optional[str] = Field(None, description="年级描述")
    sort_order: Optional[int] = Field(None, description="排序")


class GradeResponseSchema(BaseModel):
    """年级响应"""
    id: int = Field(..., description="年级ID")
    name: str = Field(..., description="年级名称")
    description: Optional[str] = Field(None, description="年级描述")
    sort_order: int = Field(..., description="排序")
    
    model_config = ConfigDict(from_attributes=True)


class GradeWithSubjectsSchema(BaseModel):
    """年级及其学科响应"""
    id: int = Field(..., description="年级ID")
    name: str = Field(..., description="年级名称")
    description: Optional[str] = Field(None, description="年级描述")
    sort_order: int = Field(..., description="排序")
    subjects: list["SubjectResponseSchema"] = Field(default_factory=list, description="学科列表")
    
    model_config = ConfigDict(from_attributes=True)


class GradeWithSubjectsAndKnowledgePointsSchema(BaseModel):
    """年级及其学科/知识点响应"""
    id: int = Field(..., description="年级ID")
    name: str = Field(..., description="年级名称")
    description: Optional[str] = Field(None, description="年级描述")
    sort_order: int = Field(..., description="排序")
    subjects: list["SubjectWithKnowledgePointsSchema"] = Field(default_factory=list, description="学科列表")
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 学科 Schema ====================

class SubjectCreateSchema(BaseModel):
    """创建学科请求"""
    name: str = Field(..., min_length=1, max_length=100, description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")
    grade_id: int = Field(..., description="所属年级ID")
    sort_order: int = Field(default=0, description="排序")


class SubjectUpdateSchema(BaseModel):
    """更新学科请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    sort_order: Optional[int] = Field(None, description="排序")


class SubjectResponseSchema(BaseModel):
    """学科响应"""
    id: int = Field(..., description="学科ID")
    name: str = Field(..., description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")
    grade_id: int = Field(..., description="所属年级ID")
    sort_order: int = Field(..., description="排序")
    
    model_config = ConfigDict(from_attributes=True)


class SubjectWithGradeSchema(BaseModel):
    """学科及其年级响应"""
    id: int = Field(..., description="学科ID")
    name: str = Field(..., description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")
    grade_id: int = Field(..., description="所属年级ID")
    sort_order: int = Field(..., description="排序")
    grade: GradeResponseSchema = Field(..., description="所属年级")
    
    model_config = ConfigDict(from_attributes=True)


class SubjectWithKnowledgePointsSchema(BaseModel):
    """学科及其知识点响应"""
    id: int = Field(..., description="学科ID")
    name: str = Field(..., description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")
    grade_id: int = Field(..., description="所属年级ID")
    sort_order: int = Field(..., description="排序")
    knowledge_points: list["KnowledgePointResponseSchema"] = Field(default_factory=list, description="知识点列表")
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 知识点 Schema ====================

class KnowledgePointCreateSchema(BaseModel):
    """创建知识点请求"""
    name: str = Field(..., min_length=1, max_length=200, description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    subject_id: int = Field(..., description="所属学科ID")
    sort_order: int = Field(default=0, description="排序")


class KnowledgePointUpdateSchema(BaseModel):
    """更新知识点请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    subject_id: Optional[int] = Field(None, description="所属学科ID")
    sort_order: Optional[int] = Field(None, description="排序")


class KnowledgePointResponseSchema(BaseModel):
    """知识点响应"""
    id: int = Field(..., description="知识点ID")
    name: str = Field(..., description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    subject_id: int = Field(..., description="所属学科ID")
    sort_order: int = Field(..., description="排序")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgePointWithSubjectSchema(BaseModel):
    """知识点及其学科响应"""
    id: int = Field(..., description="知识点ID")
    name: str = Field(..., description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    subject_id: int = Field(..., description="所属学科ID")
    sort_order: int = Field(..., description="排序")
    subject: SubjectResponseSchema = Field(..., description="所属学科")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgePointWithSubjectGradeSchema(BaseModel):
    """知识点及其学科/年级响应"""
    id: int = Field(..., description="知识点ID")
    name: str = Field(..., description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    subject_id: int = Field(..., description="所属学科ID")
    sort_order: int = Field(..., description="排序")
    subject: SubjectWithGradeSchema = Field(..., description="所属学科")
    
    model_config = ConfigDict(from_attributes=True)
