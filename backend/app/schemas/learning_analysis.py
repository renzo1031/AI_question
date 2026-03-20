"""
学习分析相关的 Schema 定义
"""
from typing import Optional
from pydantic import BaseModel, Field


class AccuracyFormattedSchema(BaseModel):
    """格式化的正确率"""
    percentage: str = Field(..., description="百分比形式，如 '85%'")
    level: str = Field(..., description="等级：优秀/良好/中等/及格/需加强")
    description: str = Field(..., description="人性化描述")


class RecentStatsSchema(BaseModel):
    """近期统计数据"""
    questions: int = Field(..., description="答题数")
    correct: int = Field(..., description="答对数")
    accuracy: float = Field(..., description="正确率（0-1）")
    accuracy_formatted: AccuracyFormattedSchema = Field(..., description="格式化的正确率")
    period: str = Field(..., description="统计周期描述")


class AllTimeStatsSchema(BaseModel):
    """全部历史统计数据"""
    questions: int = Field(..., description="总答题数")
    correct: int = Field(..., description="总答对数")
    accuracy: float = Field(..., description="总体正确率（0-1）")
    accuracy_formatted: AccuracyFormattedSchema = Field(..., description="格式化的正确率")
    period: str = Field(..., description="统计周期描述")


class Last10AccuracySchema(BaseModel):
    """最近10题正确率"""
    accuracy: float = Field(..., description="正确率（0-1）")
    accuracy_formatted: AccuracyFormattedSchema = Field(..., description="格式化的正确率")
    description: str = Field(..., description="描述")


class DailyStatsSchema(BaseModel):
    """每日统计数据"""
    answered_today: int = Field(..., description="今日答题数")
    answered_last_7_days: int = Field(..., description="最近7天答题数")


class TrendSchema(BaseModel):
    """趋势信息"""
    direction: str = Field(..., description="趋势方向：up/down/stable")
    change: str = Field(..., description="变化幅度，如 '+5%'")
    message: str = Field(..., description="趋势描述")


class LearningOverviewSchema(BaseModel):
    """学习概览数据"""
    recent_stats: RecentStatsSchema = Field(..., description="近期统计")
    all_time_stats: AllTimeStatsSchema = Field(..., description="全部历史统计")
    last_10_accuracy: Last10AccuracySchema = Field(..., description="最近10题正确率")
    daily_stats: DailyStatsSchema = Field(..., description="每日统计")
    trend: TrendSchema = Field(..., description="趋势信息")
    data_sufficient: bool = Field(..., description="数据是否充足（>=10题）")
    consecutive_days: int = Field(..., description="连续学习天数（坚持天数）")


class KnowledgeMasteryItemSchema(BaseModel):
    """知识点掌握度项"""
    knowledge_point: str = Field(..., description="知识点名称")
    mastery: float = Field(..., description="掌握度（0-1）")
    mastery_percentage: str = Field(..., description="掌握度百分比")
    mastery_level: str = Field(..., description="掌握等级")
    mastery_description: str = Field(..., description="掌握度描述")
    total_questions: int = Field(..., description="练习过的题数")
    mastered_questions: int = Field(..., description="已掌握的题数")


class KnowledgeMasteryPeriodSchema(BaseModel):
    """某时间段的知识点掌握度"""
    mastery_list: list[KnowledgeMasteryItemSchema] = Field(..., description="掌握度列表")
    period: str = Field(..., description="统计周期描述")


class KnowledgeMasterySchema(BaseModel):
    """知识点掌握度数据"""
    all_time: KnowledgeMasteryPeriodSchema = Field(..., description="全部历史掌握度")
    recent: Optional[KnowledgeMasteryPeriodSchema] = Field(None, description="近期掌握度")


class WeakPointSchema(BaseModel):
    """薄弱知识点"""
    knowledge_point: str = Field(..., description="知识点名称")
    wrong_count: int = Field(..., description="错误次数")
    total_wrong_questions: int = Field(..., description="错题数量")
    suggestion: str = Field(..., description="学习建议")
    action: str = Field(..., description="建议操作")
    action_params: dict = Field(..., description="操作参数")


class LearningSuggestionSchema(BaseModel):
    """学习建议"""
    type: str = Field(..., description="建议类型：review/practice/master")
    knowledge_point: Optional[str] = Field(None, description="相关知识点")
    message: str = Field(..., description="建议内容")
    action: Optional[str] = Field(None, description="建议操作")
    action_params: Optional[dict] = Field(None, description="操作参数")
    priority: str = Field("medium", description="优先级：high/medium/low")


class AbilityAnalysisSchema(BaseModel):
    """能力分析数据"""
    knowledge_mastery: KnowledgeMasterySchema = Field(..., description="知识点掌握度")
    weak_points: list[WeakPointSchema] = Field(..., description="薄弱知识点列表")
    suggestions: list[LearningSuggestionSchema] = Field(default=[], description="学习建议")


class FeedbackItemSchema(BaseModel):
    """反馈项"""
    type: str = Field(..., description="反馈类型：achievement/improvement/encouragement")
    message: str = Field(..., description="反馈内容")


class ProgressFeedbackSchema(BaseModel):
    """进步反馈数据"""
    feedback: list[FeedbackItemSchema] = Field(..., description="反馈列表")
