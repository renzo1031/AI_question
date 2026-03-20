"""
学习统计数据访问层
提供学习分析所需的原始数据查询
"""
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.models.question_tag import QuestionTag
from app.models.tag import SubKnowledgePoint
from app.models.user_question import UserQuestion, UserQuestionStatus


class LearningStatsRepository:
    """学习统计仓储类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def count_answered_questions(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        统计用户答题总数
        
        Args:
            user_id: 用户ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            答题总数
        """
        query = select(func.count(func.distinct(UserQuestion.question_id))).where(
            UserQuestion.user_id == user_id,
            UserQuestion.last_answer_at.isnot(None)
        )
        
        if start_time:
            query = query.where(UserQuestion.last_answer_at >= start_time)
        if end_time:
            query = query.where(UserQuestion.last_answer_at <= end_time)
        
        result = await self.session.execute(query)
        count = result.scalar() or 0
        return count
    
    async def count_correct_questions(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        统计用户答对题数
        
        Args:
            user_id: 用户ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            答对题数
        """
        query = select(func.count(func.distinct(UserQuestion.question_id))).where(
            UserQuestion.user_id == user_id,
            UserQuestion.status == UserQuestionStatus.CORRECT
        )
        
        if start_time:
            query = query.where(UserQuestion.last_answer_at >= start_time)
        if end_time:
            query = query.where(UserQuestion.last_answer_at <= end_time)
        
        result = await self.session.execute(query)
        count = result.scalar() or 0
        return count
    
    async def list_recent_answers(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[UserQuestion]:
        """
        获取用户最近的答题记录
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            最近的答题记录列表（按时间倒序）
        """
        query = (
            select(UserQuestion)
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.last_answer_at.isnot(None)
            )
            .order_by(UserQuestion.last_answer_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def list_user_questions_by_tag(
        self,
        user_id: int,
        tag: str
    ) -> list[UserQuestion]:
        """
        获取用户指定标签的答题记录
        
        Args:
            user_id: 用户ID
            tag: 标签名称
            
        Returns:
            该标签下的答题记录列表
        """
        query = (
            select(UserQuestion)
            .join(Question, UserQuestion.question_id == Question.id)
            .join(QuestionTag, Question.id == QuestionTag.question_id)
            .join(SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id)
            .where(
                UserQuestion.user_id == user_id,
                SubKnowledgePoint.name == tag
            )
        )
        
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_user_question_tag_stats(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[Tuple[str, int, str]]:
        """
        获取用户答题记录与标签的关联数据
        
        Args:
            user_id: 用户ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            列表，每项为 (tag_name, question_id, status)
        """
        query = (
            select(
                SubKnowledgePoint.name,
                UserQuestion.question_id,
                UserQuestion.status
            )
            .join(Question, UserQuestion.question_id == Question.id)
            .join(QuestionTag, Question.id == QuestionTag.question_id)
            .join(SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id)
            .where(UserQuestion.user_id == user_id)
        )
        
        if start_time:
            query = query.where(UserQuestion.last_answer_at >= start_time)
        if end_time:
            query = query.where(UserQuestion.last_answer_at <= end_time)
        
        result = await self.session.execute(query)
        return result.all()
    
    async def get_user_wrong_question_tag_stats(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[Tuple[str, int, int]]:
        """
        获取用户错题与标签的关联数据
        
        Args:
            user_id: 用户ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            列表，每项为 (tag_name, question_id, wrong_count)
        """
        query = (
            select(
                SubKnowledgePoint.name,
                UserQuestion.question_id,
                UserQuestion.wrong_count
            )
            .join(Question, UserQuestion.question_id == Question.id)
            .join(QuestionTag, Question.id == QuestionTag.question_id)
            .join(SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id)
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.status == UserQuestionStatus.WRONG
            )
        )
        
        if start_time:
            query = query.where(UserQuestion.last_answer_at >= start_time)
        if end_time:
            query = query.where(UserQuestion.last_answer_at <= end_time)
        
        result = await self.session.execute(query)
        return result.all()
    
    async def count_wrong_questions(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        统计用户错题数量
        
        Args:
            user_id: 用户ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            错题数量
        """
        query = select(func.count(func.distinct(UserQuestion.question_id))).where(
            UserQuestion.user_id == user_id,
            UserQuestion.status == UserQuestionStatus.WRONG
        )
        
        if start_time:
            query = query.where(UserQuestion.last_answer_at >= start_time)
        if end_time:
            query = query.where(UserQuestion.last_answer_at < end_time)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_daily_answer_counts(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> list[Tuple[datetime, int]]:
        """
        获取用户每日答题数量（用于计算连续学习天数）
        
        Args:
            user_id: 用户ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            列表，每项为 (日期, 答题数量)
        """
        query = (
            select(
                func.date(UserQuestion.last_answer_at).label('answer_date'),
                func.count(func.distinct(UserQuestion.question_id)).label('count')
            )
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
                UserQuestion.last_answer_at.isnot(None)
            )
            .group_by(func.date(UserQuestion.last_answer_at))
            .order_by(func.date(UserQuestion.last_answer_at).desc())
        )
        
        result = await self.session.execute(query)
        return result.all()

