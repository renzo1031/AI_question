"""
进步反馈服务
生成阶段性进步提示（情绪价值）
"""
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.learning_stats_repo import LearningStatsRepository


class ProgressFeedbackService:
    """进步反馈服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LearningStatsRepository(db)
    
    async def generate_feedback(self, user_id: int) -> list[dict]:
        """
        生成进步反馈提示
        
        触发规则：
        - 连续学习 >= 3 天
        - 最近 7 天正确率上升 >= 10%
        - 错题数量减少 >= 20%
        - 某知识点掌握度提升明显
        
        Args:
            user_id: 用户ID
            
        Returns:
            反馈列表，格式：
            [
                {
                    "type": "achievement",
                    "message": "太棒了！你已经连续学习 3 天了 🎉"
                }
            ]
        """
        feedback_list = []
        now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        
        # 1. 检查连续学习天数
        consecutive_days = await self._check_consecutive_days(user_id, now)
        if consecutive_days >= 3:
            feedback_list.append({
                "type": "achievement",
                "message": f"太棒了！你已经连续学习 {consecutive_days} 天了 🎉"
            })
        
        # 2. 检查最近7天正确率变化
        accuracy_improvement = await self._check_accuracy_improvement(user_id, now)
        if accuracy_improvement and accuracy_improvement >= 0.1:
            percentage = int(accuracy_improvement * 100)
            feedback_list.append({
                "type": "improvement",
                "message": f"最近7天你的正确率提升了 {percentage}%，进步很明显！💪"
            })
        
        # 3. 检查错题数量减少
        wrong_reduction = await self._check_wrong_reduction(user_id, now)
        if wrong_reduction and wrong_reduction >= 0.2:
            percentage = int(wrong_reduction * 100)
            feedback_list.append({
                "type": "improvement",
                "message": f"最近错题数量减少了 {percentage}%，继续保持！✨"
            })
        
        # 4. 检查今日学习情况
        today_count = await self.repo.count_answered_questions(
            user_id,
            start_time=now.replace(hour=0, minute=0, second=0, microsecond=0)
        )
        if today_count > 0:
            feedback_list.append({
                "type": "encouragement",
                "message": f"今天已经完成了 {today_count} 道题，很棒！继续加油！🚀"
            })
        
        return feedback_list
    
    async def _check_consecutive_days(self, user_id: int, now: datetime) -> int:
        """
        检查连续学习天数
        
        优化：一次性查询最近30天的答题记录，在内存中计算连续天数
        
        Args:
            user_id: 用户ID
            now: 当前时间
            
        Returns:
            连续学习天数
        """
        current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = current_date - timedelta(days=30)
        
        # 一次性查询最近30天的每日答题数量
        daily_counts = await self.repo.get_daily_answer_counts(
            user_id,
            start_time=thirty_days_ago,
            end_time=now
        )
        
        # 构建有答题的日期集合
        answered_dates = set()
        for row in daily_counts:
            answer_date = row[0]
            if isinstance(answer_date, str):
                answer_date = datetime.strptime(answer_date, '%Y-%m-%d').date()
            elif isinstance(answer_date, datetime):
                answer_date = answer_date.date()
            answered_dates.add(answer_date)
        
        # 从今天开始往前检查连续天数
        consecutive_days = 0
        check_date = current_date.date() if isinstance(current_date, datetime) else current_date
        
        for i in range(30):
            day_to_check = check_date - timedelta(days=i)
            if day_to_check in answered_dates:
                consecutive_days += 1
            else:
                break
        
        return consecutive_days
    
    async def _check_accuracy_improvement(
        self, user_id: int, now: datetime
    ) -> Optional[float]:
        """
        检查最近7天正确率变化
        
        Args:
            user_id: 用户ID
            now: 当前时间
            
        Returns:
            正确率提升幅度（0-1之间），如果没有提升则返回None
        """
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)
        
        # 最近7天的正确率
        recent_total = await self.repo.count_answered_questions(
            user_id, start_time=seven_days_ago
        )
        recent_correct = await self.repo.count_correct_questions(
            user_id, start_time=seven_days_ago
        )
        recent_accuracy = (
            recent_correct / recent_total if recent_total > 0 else 0.0
        )
        
        # 前7天（7-14天前）的正确率
        previous_total = await self.repo.count_answered_questions(
            user_id, start_time=fourteen_days_ago, end_time=seven_days_ago
        )
        previous_correct = await self.repo.count_correct_questions(
            user_id, start_time=fourteen_days_ago, end_time=seven_days_ago
        )
        previous_accuracy = (
            previous_correct / previous_total if previous_total > 0 else 0.0
        )
        
        # 计算提升幅度
        if previous_accuracy > 0 and recent_accuracy > previous_accuracy:
            improvement = recent_accuracy - previous_accuracy
            return improvement
        
        return None
    
    async def _check_wrong_reduction(
        self, user_id: int, now: datetime
    ) -> Optional[float]:
        """
        检查错题数量减少情况
        
        Args:
            user_id: 用户ID
            now: 当前时间
            
        Returns:
            错题减少比例（0-1之间），如果没有减少则返回None
        """
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)
        
        # 通过 Repository 查询错题数量
        recent_wrong = await self.repo.count_wrong_questions(
            user_id, start_time=seven_days_ago
        )
        previous_wrong = await self.repo.count_wrong_questions(
            user_id, start_time=fourteen_days_ago, end_time=seven_days_ago
        )
        
        # 计算减少比例
        if previous_wrong > 0 and recent_wrong < previous_wrong:
            reduction = (previous_wrong - recent_wrong) / previous_wrong
            return reduction
        
        return None

