"""
题目选项模型
定义题目的选项（如选择题的A、B、C、D选项）
"""
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.question import Question


class QuestionOption(Base):
    """题目选项表"""
    
    __tablename__ = "question_options"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="选项ID"
    )
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True, comment="题目ID"
    )
    option_key: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="选项标识（如A、B、C、D或1、2、3、4）"
    )
    option_text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="选项内容"
    )
    
    # 关系
    question: Mapped["Question"] = relationship("Question", back_populates="options")
    
    def __repr__(self) -> str:
        return f"<QuestionOption(id={self.id}, question_id={self.question_id}, option_key={self.option_key})>"

