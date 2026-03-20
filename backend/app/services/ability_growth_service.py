"""
能力成长服务
计算学生能力成长和薄弱点分析
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.learning_stats_repo import LearningStatsRepository
from app.models.user_question import UserQuestionStatus


class AbilityGrowthService:
    """能力成长服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LearningStatsRepository(db)
    
    async def get_knowledge_mastery(
        self,
        user_id: int,
        time_window_days: Optional[int] = None
    ) -> dict:
        """
        获取知识点掌握度统计
        
        规则：
        - 按 tags（知识点）统计
        - 掌握度 = 已掌握题数 / 练习过的题数
        - 已掌握题：status = correct
        - 练习过的题：user_question 中出现过
        
        Args:
            user_id: 用户ID
            time_window_days: 时间窗口（天数），None表示全部历史
            
        Returns:
            知识点掌握度数据，包含近期和全部历史
        """
        now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        
        # 计算时间范围
        recent_start = now - timedelta(days=time_window_days) if time_window_days else None
        
        # 获取近期数据（如果指定了时间窗口）
        recent_mastery = None
        if time_window_days:
            recent_rows = await self.repo.get_user_question_tag_stats(
                user_id, start_time=recent_start
            )
            recent_mastery = self._calculate_mastery_from_rows(recent_rows)
        
        # 获取全部历史数据
        all_rows = await self.repo.get_user_question_tag_stats(user_id)
        all_time_mastery = self._calculate_mastery_from_rows(all_rows)
        
        # 构建返回结果
        result = {
            "all_time": {
                "mastery_list": all_time_mastery,
                "period": "全部历史"
            }
        }
        
        if recent_mastery is not None:
            result["recent"] = {
                "mastery_list": recent_mastery,
                "period": f"最近{time_window_days}天"
            }
        
        return result
    
    def _calculate_mastery_from_rows(self, rows: list) -> list[dict]:
        """
        从查询结果计算掌握度
        
        Args:
            rows: 查询结果列表，每项为 (tag_name, question_id, status)
            
        Returns:
            知识点掌握度列表
        """
        # 按标签统计
        tag_stats = defaultdict(lambda: {"total": 0, "mastered": 0})
        
        # 用于去重：同一个题目在同一个标签下只统计一次
        seen_questions = defaultdict(set)
        
        for tag_name, question_id, status in rows:
            # 检查是否已经统计过这个题目在这个标签下
            if question_id not in seen_questions[tag_name]:
                seen_questions[tag_name].add(question_id)
                tag_stats[tag_name]["total"] += 1
                if status == UserQuestionStatus.CORRECT:
                    tag_stats[tag_name]["mastered"] += 1
        
        # 构建返回结果
        mastery_list = []
        for tag_name, stats in tag_stats.items():
            total = stats["total"]
            mastered = stats["mastered"]
            mastery = round(mastered / total, 4) if total > 0 else 0.0
            
            # 添加人性化描述
            mastery_info = self._format_mastery(mastery)
            
            mastery_list.append({
                "knowledge_point": tag_name,
                "mastery": mastery,
                "mastery_percentage": mastery_info["percentage"],
                "mastery_level": mastery_info["level"],
                "mastery_description": mastery_info["description"],
                "total_questions": total,
                "mastered_questions": mastered
            })
        
        # 按掌握度降序排序
        mastery_list.sort(key=lambda x: x["mastery"], reverse=True)
        
        return mastery_list
    
    def _format_mastery(self, mastery: float) -> dict:
        """
        格式化掌握度为人性化描述
        
        Args:
            mastery: 掌握度（0-1）
            
        Returns:
            包含百分比、等级和描述的字典
        """
        percentage = int(mastery * 100)
        if percentage >= 90:
            level = "优秀"
            description = "掌握得非常好！"
        elif percentage >= 80:
            level = "良好"
            description = "掌握得不错，继续保持！"
        elif percentage >= 70:
            level = "中等"
            description = "还有提升空间，加油！"
        elif percentage >= 60:
            level = "及格"
            description = "需要多加练习"
        else:
            level = "需加强"
            description = "建议重点复习这个知识点"
        
        return {
            "percentage": f"{percentage}%",
            "level": level,
            "description": description
        }
    
    async def get_weak_points(
        self,
        user_id: int,
        threshold: int = 2,
        time_window_days: Optional[int] = None
    ) -> list[dict]:
        """
        获取薄弱知识点列表
        
        规则：
        - wrong_count 高
        - status = wrong
        - 连续答对次数 < 阈值（这里简化为：错题数量 >= threshold）
        
        Args:
            user_id: 用户ID
            threshold: 错题数量阈值，默认2
            time_window_days: 时间窗口（天数），None表示全部历史
            
        Returns:
            薄弱知识点列表，包含学习建议
        """
        now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
        start_time = now - timedelta(days=time_window_days) if time_window_days else None
        
        # 通过 Repository 获取错题数据
        rows = await self.repo.get_user_wrong_question_tag_stats(
            user_id, start_time=start_time
        )
        
        # 按标签统计错题
        tag_wrong_stats = defaultdict(lambda: {"wrong_count": 0, "question_ids": set()})
        
        for tag_name, question_id, wrong_count in rows:
            tag_wrong_stats[tag_name]["wrong_count"] += wrong_count
            tag_wrong_stats[tag_name]["question_ids"].add(question_id)
        
        # 构建返回结果，只返回错题数量 >= threshold 的知识点
        weak_points = []
        for tag_name, stats in tag_wrong_stats.items():
            total_wrong_questions = len(stats["question_ids"])
            wrong_count = stats["wrong_count"]
            
            # 筛选：错题数量 >= threshold
            if total_wrong_questions >= threshold:
                weak_points.append({
                    "knowledge_point": tag_name,
                    "wrong_count": wrong_count,
                    "total_wrong_questions": total_wrong_questions,
                    "suggestion": f"建议重点复习「{tag_name}」相关题目",
                    "action": "practice",
                    "action_params": {"tags": [tag_name]}
                })
        
        # 按错题数量降序排序
        weak_points.sort(key=lambda x: x["wrong_count"], reverse=True)
        
        return weak_points
    
    async def get_learning_suggestions(self, user_id: int, limit: int = 3) -> list[dict]:
        """
        生成学习建议
        
        Args:
            user_id: 用户ID
            limit: 返回建议数量限制
            
        Returns:
            学习建议列表
        """
        suggestions = []
        
        # 基于薄弱知识点生成建议
        weak_points = await self.get_weak_points(user_id, time_window_days=30)
        for point in weak_points[:limit]:
            suggestions.append({
                "type": "review",
                "knowledge_point": point["knowledge_point"],
                "message": point["suggestion"],
                "action": point["action"],
                "action_params": point["action_params"],
                "priority": "high" if point["wrong_count"] >= 5 else "medium"
            })
        
        return suggestions

