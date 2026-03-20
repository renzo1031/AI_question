
"""题目模型
定义题库相关的数据库模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.grade_knowledge import Grade, Subject, KnowledgePoint
    from app.models.tag import SubKnowledgePoint
    from app.models.user_question import UserQuestion
    from app.models.question_option import QuestionOption


class Question(Base):
    """题目表"""
    
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="题目ID"
    )
    
    # 题目内容
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="题目内容"
    )
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True, comment="题目内容哈希（SHA256）"
    )
    
    # 题目属性
    question_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="题目类型"
    )
    difficulty: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="难度等级"
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="来源"
    )
    
    # 外键关联（优先使用）
    grade_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("grades.id", ondelete="SET NULL"), 
        nullable=True, index=True, comment="所属年级ID"
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("subjects.id", ondelete="SET NULL"), 
        nullable=True, index=True, comment="所属学科ID"
    )
    knowledge_point_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("knowledge_points.id", ondelete="SET NULL"), 
        nullable=True, index=True, comment="所属知识点ID"
    )
    
    # 字符串字段（兼容旧数据，逐步废弃）
    grade: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="年级（兼容字段）"
    )
    subject: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="科目（兼容字段）"
    )
    knowledge_point: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="知识点（兼容字段）"
    )
    
    # AI相关
    ai_answer: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="AI答案"
    )
    ai_analysis: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="AI解析"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    
    # 关系
    grade_obj: Mapped[Optional["Grade"]] = relationship(
        "Grade", foreign_keys=[grade_id]
    )
    subject_obj: Mapped[Optional["Subject"]] = relationship(
        "Subject", foreign_keys=[subject_id]
    )
    knowledge_point_obj: Mapped[Optional["KnowledgePoint"]] = relationship(
        "KnowledgePoint", foreign_keys=[knowledge_point_id]
    )
    options: Mapped[list["QuestionOption"]] = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )
    sub_knowledge_points: Mapped[list["SubKnowledgePoint"]] = relationship(
        "SubKnowledgePoint", secondary="question_tags", back_populates="questions"
    )
    user_questions: Mapped[list["UserQuestion"]] = relationship(
        "UserQuestion", back_populates="question"
    )
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, content_hash={self.content_hash})>"
