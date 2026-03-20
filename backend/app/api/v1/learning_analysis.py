"""
学习分析API路由
提供学习分析、能力成长、进步反馈等接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.middleware.auth import get_current_user_id
from app.services.ability_growth_service import AbilityGrowthService
from app.services.learning_stats_service import LearningStatsService
from app.services.progress_feedback_service import ProgressFeedbackService

# 创建学习分析路由
router = APIRouter(prefix="/learning", tags=["学习分析"])


@router.get("/overview", summary="获取学习概览", dependencies=[Depends(jwt_security)])
async def get_learning_overview(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    time_window_days: int = Query(default=30, ge=1, le=365, description="时间窗口（天数），默认30天")
):
    """
    获取学习概览数据
    
    返回内容：
    - recent_stats: 近期统计（根据 time_window_days 参数）
    - all_time_stats: 全部历史统计
    - last_10_accuracy: 最近10题正确率
    - daily_stats: 今日和最近7天答题数
    - trend: 学习趋势（进步/稳定/需加油）
    - data_sufficient: 数据是否充足
    
    需要JWT Token认证
    """
    service = LearningStatsService(db)
    overview = await service.get_learning_overview(user_id, time_window_days)
    return success(data=overview)


@router.get("/ability", summary="获取能力分析", dependencies=[Depends(jwt_security)])
async def get_ability_analysis(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    time_window_days: Optional[int] = Query(default=None, ge=1, le=365, description="时间窗口（天数），None表示全部历史")
):
    """
    获取能力成长分析
    
    返回内容：
    - knowledge_mastery: 知识点掌握度（包含全部历史和近期数据）
    - weak_points: 薄弱知识点列表（包含学习建议）
    - suggestions: 学习建议列表
    
    需要JWT Token认证
    """
    service = AbilityGrowthService(db)
    knowledge_mastery = await service.get_knowledge_mastery(user_id, time_window_days)
    weak_points = await service.get_weak_points(user_id, time_window_days=time_window_days)
    suggestions = await service.get_learning_suggestions(user_id)
    
    return success(data={
        "knowledge_mastery": knowledge_mastery,
        "weak_points": weak_points,
        "suggestions": suggestions
    })


@router.get("/feedback", summary="获取进步反馈", dependencies=[Depends(jwt_security)])
async def get_progress_feedback(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取进步反馈提示
    
    返回内容：
    - feedback: 反馈列表，包含成就、进步、鼓励等类型的消息
    
    需要JWT Token认证
    """
    service = ProgressFeedbackService(db)
    feedback = await service.generate_feedback(user_id)
    
    return success(data={"feedback": feedback})

