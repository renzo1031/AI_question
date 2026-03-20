"""
年级和知识点模型
定义年级、学科、知识点的层级关系
"""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tag import SubKnowledgePoint


class Grade(Base):
    """年级表"""
    
    __tablename__ = "grades"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="年级ID"
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True, comment="年级名称（如：一年级、七年级、高一）"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="年级描述"
    )
    sort_order: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="排序（值越小越靠前）"
    )
    
    # 关系
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="grade", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Grade(id={self.id}, name={self.name})>"


class Subject(Base):
    """学科表"""
    
    __tablename__ = "subjects"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="学科ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="学科名称（如：数学、语文）"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="学科描述"
    )
    grade_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属年级ID"
    )
    sort_order: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="排序（值越小越靠前）"
    )
    
    # 关系
    grade: Mapped["Grade"] = relationship("Grade", back_populates="subjects")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(
        "KnowledgePoint", back_populates="subject", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name={self.name}, grade_id={self.grade_id})>"


class KnowledgePoint(Base):
    """知识点表"""
    
    __tablename__ = "knowledge_points"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="知识点ID"
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="知识点名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="知识点描述"
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属学科ID"
    )
    sort_order: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="排序（值越小越靠前）"
    )
    
    # 关系
    subject: Mapped["Subject"] = relationship("Subject", back_populates="knowledge_points")
    sub_knowledge_points: Mapped[List["SubKnowledgePoint"]] = relationship(
        "SubKnowledgePoint", back_populates="knowledge_point", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgePoint(id={self.id}, name={self.name}, subject_id={self.subject_id})>"
