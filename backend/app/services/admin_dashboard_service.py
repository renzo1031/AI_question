from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_dashboard_repo import AdminDashboardRepository
from app.schemas.admin_dashboard import (
    DashboardOverviewSchema,
    HotKnowledgePointSchema,
    RecentUserSchema,
    TimeSeriesPointSchema,
)


class AdminDashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminDashboardRepository(db)

    @staticmethod
    def _build_date_series(start_date: date, end_date: date) -> list[date]:
        days: list[date] = []
        cur = start_date
        while cur <= end_date:
            days.append(cur)
            cur = cur + timedelta(days=1)
        return days

    @staticmethod
    def _to_date(value) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        return value

    async def get_overview(self, period_days: int = 30) -> DashboardOverviewSchema:
        now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        end_time = now
        start_time = now - timedelta(days=period_days)

        start_date = start_time.date()
        end_date = end_time.date()
        full_days = self._build_date_series(start_date, end_date)

        # timeseries
        new_users_rows = await self.repo.get_new_users_by_day(start_time, end_time)
        active_users_rows = await self.repo.get_active_users_by_day(start_time, end_time)
        answered_rows = await self.repo.get_answered_questions_by_day(start_time, end_time)
        accuracy_rows = await self.repo.get_accuracy_by_day(start_time, end_time)

        new_users_map = {self._to_date(d): int(v or 0) for d, v in new_users_rows}
        active_users_map = {self._to_date(d): int(v or 0) for d, v in active_users_rows}
        answered_map = {self._to_date(d): int(v or 0) for d, v in answered_rows}
        accuracy_map = {self._to_date(d): float(v or 0.0) for d, v in accuracy_rows}

        new_users_series = [TimeSeriesPointSchema(day=day, value=float(new_users_map.get(day, 0))) for day in full_days]
        active_users_series = [TimeSeriesPointSchema(day=day, value=float(active_users_map.get(day, 0))) for day in full_days]
        answered_series = [TimeSeriesPointSchema(day=day, value=float(answered_map.get(day, 0))) for day in full_days]
        accuracy_series = [TimeSeriesPointSchema(day=day, value=float(accuracy_map.get(day, 0.0))) for day in full_days]

        # summary
        total_users = await self.repo.count_total_users()
        summary_new_users = await self.repo.count_new_users(start_time, end_time)
        summary_active_users = await self.repo.count_active_users_distinct(start_time, end_time)
        summary_answered_questions = await self.repo.count_answered_questions(start_time, end_time)
        summary_correct = await self.repo.count_correct_questions(start_time, end_time)
        summary_accuracy = round(summary_correct / summary_answered_questions, 4) if summary_answered_questions > 0 else 0.0

        # 热门知识点
        hot_points_data = await self.repo.get_hot_knowledge_points(start_time, end_time, limit=5)
        hot_knowledge_points = [
            HotKnowledgePointSchema(
                name=name,
                answer_count=answer_count,
                wrong_count=wrong_count,
                wrong_rate=wrong_rate
            )
            for name, answer_count, wrong_count, wrong_rate in hot_points_data
        ]
        
        # 最新注册用户
        recent_users_data = await self.repo.get_recent_users(limit=5)
        recent_users = [
            RecentUserSchema(
                id=user.id,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at
            )
            for user in recent_users_data
        ]

        notes = None
        if summary_answered_questions < 50:
            notes = "近30天答题量较少，趋势仅供参考"

        return DashboardOverviewSchema(
            period_days=period_days,
            start_date=start_date,
            end_date=end_date,
            new_users=new_users_series,
            active_users=active_users_series,
            answered_questions=answered_series,
            accuracy=accuracy_series,
            total_users=total_users,
            summary_new_users=summary_new_users,
            summary_active_users=summary_active_users,
            summary_answered_questions=summary_answered_questions,
            summary_accuracy=summary_accuracy,
            hot_knowledge_points=hot_knowledge_points,
            recent_users=recent_users,
            notes=notes,
        )
