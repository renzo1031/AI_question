from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimeSeriesPointSchema(BaseModel):
    day: date = Field(..., description="日期")
    value: float = Field(..., description="数值")


class HotKnowledgePointSchema(BaseModel):
    """热门知识点Schema"""
    name: str = Field(..., description="知识点名称")
    answer_count: int = Field(..., description="答题次数")
    wrong_count: int = Field(..., description="错误次数")
    wrong_rate: float = Field(..., description="错误率（0-1）")


class RecentUserSchema(BaseModel):
    """最新用户Schema"""
    id: UUID = Field(..., description="用户ID")
    phone: Optional[str] = Field(None, description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")
    created_at: datetime = Field(..., description="注册时间")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardOverviewSchema(BaseModel):
    period_days: int = Field(..., description="统计周期天数")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")

    new_users: list[TimeSeriesPointSchema] = Field(default_factory=list, description="新增用户（按天）")
    active_users: list[TimeSeriesPointSchema] = Field(default_factory=list, description="活跃用户（按天）")
    answered_questions: list[TimeSeriesPointSchema] = Field(default_factory=list, description="答题量（按天）")
    accuracy: list[TimeSeriesPointSchema] = Field(default_factory=list, description="正确率（按天，0-1）")

    total_users: int = Field(0, description="总用户数")
    summary_new_users: int = Field(0, description="周期内新增用户")
    summary_active_users: int = Field(0, description="周期内活跃用户（去重）")
    summary_answered_questions: int = Field(0, description="周期内答题量")
    summary_accuracy: float = Field(0.0, description="周期内整体正确率（0-1）")
    
    hot_knowledge_points: list[HotKnowledgePointSchema] = Field(default_factory=list, description="热门知识点Top5")
    recent_users: list[RecentUserSchema] = Field(default_factory=list, description="最新注册用户（5个）")

    notes: Optional[str] = Field(None, description="备注")
