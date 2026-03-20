"""
题目纠错模型
用于记录用户提交的题目纠错信息
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.user import User


class QuestionCorrection(Base):
    """题目纠错表"""
    
    __tablename__ = "question_corrections"
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="纠错记录ID"
    )
    
    # 关联字段
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False, index=True, comment="题目ID"
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True, comment="提交用户ID"
    )
    
    # 纠错内容
    reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="纠错原因/描述"
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", 
        index=True, comment="状态：pending(待处理)/resolved(已解决)/ignored(已忽略)"
    )
    
    # 管理员处理信息
    admin_note: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="管理员备注"
    )
    handled_by: Mapped[Optional[str]] = mapped_column(
        UUID, nullable=True, comment="处理人ID（管理员ID）"
    )
    handled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="处理时间"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), 
        onupdate=func.now(), comment="更新时间"
    )
    
    # 关系
    question: Mapped["Question"] = relationship("Question", foreign_keys=[question_id])
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    # 注意: handled_by 是管理员ID，不在 users 表中，所以没有 relationship
    
    def __repr__(self) -> str:
        return f"<QuestionCorrection(id={self.id}, question_id={self.question_id}, status={self.status})>"
