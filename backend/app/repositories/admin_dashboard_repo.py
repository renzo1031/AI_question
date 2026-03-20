from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_question import UserQuestion, UserQuestionStatus
from app.models.tag import SubKnowledgePoint
from app.models.question import Question


class AdminDashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_new_users_by_day(self, start_time: datetime, end_time: datetime) -> list[tuple[datetime, int]]:
        query = (
            select(
                func.date(User.created_at).label("day"),
                func.count(User.id).label("count"),
            )
            .where(User.created_at >= start_time, User.created_at <= end_time)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at).asc())
        )
        result = await self.db.execute(query)
        return result.all()

    async def count_new_users(self, start_time: datetime, end_time: datetime) -> int:
        result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= start_time, User.created_at <= end_time)
        )
        return result.scalar() or 0
    
    async def count_total_users(self) -> int:
        """查询总用户数"""
        result = await self.db.execute(
            select(func.count(User.id))
        )
        return result.scalar() or 0

    async def get_active_users_by_day(self, start_time: datetime, end_time: datetime) -> list[tuple[datetime, int]]:
        query = (
            select(
                func.date(UserQuestion.last_answer_at).label("day"),
                func.count(func.distinct(UserQuestion.user_id)).label("count"),
            )
            .where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
            .group_by(func.date(UserQuestion.last_answer_at))
            .order_by(func.date(UserQuestion.last_answer_at).asc())
        )
        result = await self.db.execute(query)
        return result.all()

    async def count_active_users_distinct(self, start_time: datetime, end_time: datetime) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(UserQuestion.user_id))).where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
        )
        return result.scalar() or 0

    async def get_answered_questions_by_day(self, start_time: datetime, end_time: datetime) -> list[tuple[datetime, int]]:
        query = (
            select(
                func.date(UserQuestion.last_answer_at).label("day"),
                func.count(UserQuestion.question_id).label("count"),
            )
            .where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
            .group_by(func.date(UserQuestion.last_answer_at))
            .order_by(func.date(UserQuestion.last_answer_at).asc())
        )
        result = await self.db.execute(query)
        return result.all()

    async def count_answered_questions(self, start_time: datetime, end_time: datetime) -> int:
        result = await self.db.execute(
            select(func.count(UserQuestion.question_id)).where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
        )
        return result.scalar() or 0

    async def count_correct_questions(self, start_time: datetime, end_time: datetime) -> int:
        result = await self.db.execute(
            select(func.count(UserQuestion.question_id)).where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.status == UserQuestionStatus.CORRECT,
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
        )
        return result.scalar() or 0

    async def get_accuracy_by_day(self, start_time: datetime, end_time: datetime) -> list[tuple[datetime, float]]:
        total_subq = (
            select(
                func.date(UserQuestion.last_answer_at).label("day"),
                func.count(UserQuestion.question_id).label("total"),
            )
            .where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
            .group_by(func.date(UserQuestion.last_answer_at))
            .subquery()
        )

        correct_subq = (
            select(
                func.date(UserQuestion.last_answer_at).label("day"),
                func.count(UserQuestion.question_id).label("correct"),
            )
            .where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.status == UserQuestionStatus.CORRECT,
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time,
            )
            .group_by(func.date(UserQuestion.last_answer_at))
            .subquery()
        )

        query = (
            select(
                total_subq.c.day,
                (func.coalesce(correct_subq.c.correct, 0) / func.nullif(total_subq.c.total, 0)).label("accuracy"),
            )
            .select_from(total_subq)
            .outerjoin(correct_subq, correct_subq.c.day == total_subq.c.day)
            .order_by(total_subq.c.day.asc())
        )

        result = await self.db.execute(query)
        rows = result.all()
        # accuracy 可能为 None（除0），转为 0.0
        return [(day, float(acc or 0.0)) for day, acc in rows]
    
    async def get_hot_knowledge_points(self, start_time: datetime, end_time: datetime, limit: int = 5) -> list[tuple[str, int, int, float]]:
        """
        获取热门知识点（按答题次数排序）
        返回：(知识点名称, 答题次数, 错误次数, 错误率)
        """
        from app.models.question_tag import QuestionTag
        
        # 统计每个知识点的答题次数和错误次数
        query = (
            select(
                SubKnowledgePoint.name,
                func.count(UserQuestion.question_id).label("answer_count"),
                func.sum(
                    case(
                        (UserQuestion.status == UserQuestionStatus.WRONG, 1),
                        else_=0
                    )
                ).label("wrong_count")
            )
            .select_from(UserQuestion)
            .join(Question, UserQuestion.question_id == Question.id)
            .join(QuestionTag, QuestionTag.question_id == Question.id)
            .join(SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id)
            .where(
                UserQuestion.last_answer_at.isnot(None),
                UserQuestion.last_answer_at >= start_time,
                UserQuestion.last_answer_at <= end_time
            )
            .group_by(SubKnowledgePoint.name)
            .order_by(func.count(UserQuestion.question_id).desc())
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 计算错误率
        hot_points = []
        for name, answer_count, wrong_count in rows:
            answer_count = int(answer_count or 0)
            wrong_count = int(wrong_count or 0)
            wrong_rate = round(wrong_count / answer_count, 4) if answer_count > 0 else 0.0
            hot_points.append((name, answer_count, wrong_count, wrong_rate))
        
        return hot_points
    
    async def get_recent_users(self, limit: int = 5) -> list[User]:
        """
        获取最新注册的用户
        """
        query = (
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
