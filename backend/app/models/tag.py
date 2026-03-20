"""
次知识点模型
定义题目的次知识点（细分知识点），建立三层知识体系：年级 → 知识点 → 次知识点
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.grade_knowledge import KnowledgePoint


class SubKnowledgePoint(Base):
    """次知识点表（原标签表）"""
    
    __tablename__ = "tags"  # 保持表名不变，避免数据迁移
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="次知识点ID"
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="次知识点名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="次知识点描述"
    )
    knowledge_point_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("knowledge_points.id", ondelete="CASCADE"), 
        nullable=True, index=True, comment="所属知识点ID"
    )
    sort_order: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="排序（值越小越靠前）"
    )
    
    # 关系
    knowledge_point: Mapped[Optional["KnowledgePoint"]] = relationship(
        "KnowledgePoint", back_populates="sub_knowledge_points"
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question", secondary="question_tags", back_populates="sub_knowledge_points"
    )
    
    def __repr__(self) -> str:
        return f"<SubKnowledgePoint(id={self.id}, name={self.name}, knowledge_point_id={self.knowledge_point_id})>"

