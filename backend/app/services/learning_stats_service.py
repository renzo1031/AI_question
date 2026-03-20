"""
学习统计服务
计算基础学习数据统计
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_question import UserQuestionStatus
from app.repositories.learning_stats_repo import LearningStatsRepository


class LearningStatsService:
    """学习统计服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LearningStatsRepository(db)
    
    async def get_learning_overview(
        self,
        user_id: int,
        time_window_days: int = 30
    ) -> dict:
        """
        获取学习概览数据（支持时间窗口）
        
        Args:
            user_id: 用户ID
            time_window_days: 时间窗口（天数），默认30天
            
        Returns:
            学习概览数据，包含近期和全部历史数据
        """
        now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seven_days_ago = now - timedelta(days=7)
        window_start = now - timedelta(days=time_window_days)
        
        # === 全部历史数据 ===
        total_questions = await self.repo.count_answered_questions(user_id)
        total_correct = await self.repo.count_correct_questions(user_id)
        overall_accuracy = (
            round(total_correct / total_questions, 4) if total_questions > 0 else 0.0
        )
        
        # === 最近 N 天数据 ===
        recent_questions = await self.repo.count_answered_questions(
            user_id, start_time=window_start
        )
        recent_correct = await self.repo.count_correct_questions(
            user_id, start_time=window_start
        )
        recent_accuracy = (
            round(recent_correct / recent_questions, 4) if recent_questions > 0 else 0.0
        )
        
        # === 最近10题正确率 ===
        recent_answers = await self.repo.list_recent_answers(user_id, limit=10)
        last_10_correct = sum(
            1 for uq in recent_answers if uq.status == UserQuestionStatus.CORRECT
        )
        last_10_accuracy = (
            round(last_10_correct / len(recent_answers), 4) if recent_answers else 0.0
        )
        
        # === 今日和最近7天答题数 ===
        answered_today = await self.repo.count_answered_questions(
            user_id, start_time=today_start
        )
        answered_last_7_days = await self.repo.count_answered_questions(
            user_id, start_time=seven_days_ago
        )
        
        # === 计算连续学习天数 ===
        consecutive_days = await self._calculate_consecutive_days(user_id, now)
        
        # === 计算趋势 ===
        trend = self._calculate_trend(overall_accuracy, recent_accuracy)
        
        # === 构建返回结果 ===
        return {
            "recent_stats": {
                "questions": recent_questions,
                "correct": recent_correct,
                "accuracy": recent_accuracy,
                "accuracy_formatted": self._format_accuracy(recent_accuracy),
                "period": f"最近{time_window_days}天"
            },
            "all_time_stats": {
                "questions": total_questions,
                "correct": total_correct,
                "accuracy": overall_accuracy,
                "accuracy_formatted": self._format_accuracy(overall_accuracy),
                "period": "全部历史"
            },
            "last_10_accuracy": {
                "accuracy": last_10_accuracy,
                "accuracy_formatted": self._format_accuracy(last_10_accuracy),
                "description": "最近10题正确率"
            },
            "daily_stats": {
                "answered_today": answered_today,
                "answered_last_7_days": answered_last_7_days
            },
            "trend": trend,
            "data_sufficient": total_questions >= 10,
            "consecutive_days": consecutive_days
        }
    
    def _format_accuracy(self, accuracy: float) -> dict:
        """
        格式化正确率为人性化描述
        
        Args:
            accuracy: 正确率（0-1）
            
        Returns:
            包含百分比、等级和描述的字典
        """
        percentage = int(accuracy * 100)
        if percentage >= 90:
            level = "优秀"
            description = f"你的正确率是{percentage}%，非常棒！"
        elif percentage >= 80:
            level = "良好"
            description = f"你的正确率是{percentage}%，继续保持！"
        elif percentage >= 70:
            level = "中等"
            description = f"你的正确率是{percentage}%，还有提升空间"
        elif percentage >= 60:
            level = "及格"
            description = f"你的正确率是{percentage}%，需要多加练习"
        else:
            level = "需加强"
            description = f"你的正确率是{percentage}%，建议重点复习"
        
        return {
            "percentage": f"{percentage}%",
            "level": level,
            "description": description
        }
    
    async def _calculate_consecutive_days(
        self,
        user_id: int,
        now: datetime
    ) -> int:
        """
        计算连续学习天数（坚持天数）
        
        从最近一次答题的日期开始往前数，看有多少天连续有答题记录。
        
        Args:
            user_id: 用户ID
            now: 当前时间
            
        Returns:
            连续学习天数
        """
        # 查询最近365天的每日答题记录
        start_time = now - timedelta(days=365)
        daily_counts = await self.repo.get_daily_answer_counts(
            user_id, start_time, now
        )
        
        if not daily_counts:
            return 0
        
        # 构建有答题记录的日期集合（func.date() 返回的是 date 类型）
        answered_dates = set()
        for date_obj, count in daily_counts:
            # func.date() 返回的是 date 类型，但有时可能是 datetime，统一处理
            if isinstance(date_obj, datetime):
                answered_dates.add(date_obj.date())
            elif isinstance(date_obj, date):
                answered_dates.add(date_obj)
            else:
                # 如果是其他类型，尝试转换
                answered_dates.add(date_obj)
        
        if not answered_dates:
            return 0
        
        # 找到最近有答题的日期
        max_date = max(answered_dates)
        today = now.date()
        
        # 如果最近答题日期距离今天超过1天，说明已经中断，返回0
        # 允许今天或昨天有答题记录才算连续
        if max_date < today - timedelta(days=1):
            return 0
        
        # 从最近有答题的日期开始往前数连续天数
        consecutive = 0
        current_date = max_date
        
        # 往前数连续天数，直到遇到没有答题记录的那一天
        while current_date in answered_dates:
            consecutive += 1
            current_date = current_date - timedelta(days=1)
            # 防止无限循环，最多检查365天
            if consecutive >= 365:
                break
        
        return consecutive
    
    def _calculate_trend(
        self,
        all_time_accuracy: float,
        recent_accuracy: float
    ) -> dict:
        """
        计算学习趋势
        
        Args:
            all_time_accuracy: 全部历史正确率
            recent_accuracy: 近期正确率
            
        Returns:
            趋势信息字典
        """
        diff = recent_accuracy - all_time_accuracy
        diff_percentage = int(abs(diff) * 100)
        
        if diff > 0.05:
            direction = "up"
            message = f"近期正确率比历史平均高{diff_percentage}%，进步明显！"
        elif diff < -0.05:
            direction = "down"
            message = f"近期正确率比历史平均低{diff_percentage}%，需要加油"
        else:
            direction = "stable"
            message = "近期表现稳定，继续保持"
        
        return {
            "direction": direction,
            "change": f"{'+' if diff > 0 else ''}{diff_percentage}%" if diff != 0 else "0%",
            "message": message
        }

