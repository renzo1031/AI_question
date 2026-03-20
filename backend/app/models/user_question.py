"""
用户-题目关系模型
记录用户对题目的练习状态、答案、错题统计等
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

import uuid

from sqlalchemy import BigInteger, DateTime, Enum as SQLEnum, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.user import User


class UserQuestionStatus(str, Enum):
    """用户题目状态"""
    WRONG = "wrong"      # 答错
    CORRECT = "correct"  # 答对
    FAVORITE = "favorite"  # 收藏


class UserQuestion(Base):
    """用户-题目关系表"""
    
    __tablename__ = "user_questions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户ID"
    )
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True, comment="题目ID"
    )
    
    # 状态
    status: Mapped[Optional[UserQuestionStatus]] = mapped_column(
        SQLEnum(UserQuestionStatus), nullable=True, comment="状态（wrong/correct/favorite）"
    )
    
    # 练习统计
    wrong_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="错误次数"
    )
    
    # 答案记录
    last_answer: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="最后一次答案"
    )
    last_answer_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="最后一次答题时间"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="user_questions")
    question: Mapped["Question"] = relationship("Question", back_populates="user_questions")
    
    # 联合唯一约束（虽然联合主键已经保证了唯一性，但可以添加索引优化查询）
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )
    
    def __repr__(self) -> str:
        return f"<UserQuestion(user_id={self.user_id}, question_id={self.question_id}, status={self.status})>"

