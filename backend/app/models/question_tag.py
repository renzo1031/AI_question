"""
题目标签关联表
题目和标签的多对多关系中间表
"""
from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionTag(Base):
    """题目标签关联表"""
    
    __tablename__ = "question_tags"
    
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True, comment="题目ID"
    )
    tag_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, comment="标签ID"
    )
    
    # 联合唯一约束（虽然联合主键已经保证了唯一性，但可以添加索引优化查询）
    __table_args__ = (
        UniqueConstraint("question_id", "tag_id", name="uq_question_tag"),
    )
    
    def __repr__(self) -> str:
        return f"<QuestionTag(question_id={self.question_id}, tag_id={self.tag_id})>"

