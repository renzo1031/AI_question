"""统一操作日志模型 - 包含管理员和用户日志"""
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OperationLog(Base):
    """统一操作日志表"""
    
    __tablename__ = "operation_logs"
    
    # 基本信息
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="日志ID"
    )
    
    # 用户信息
    user_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="用户类型：admin/user"
    )
    
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="用户ID（管理员或普通用户）"
    )
    
    username: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="用户名（管理员用户名或用户手机号）"
    )
    
    # 日志级别和分类
    log_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="INFO",
        comment="日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL"
    )
    
    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="所属模块"
    )
    
    action: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="操作动作"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="操作描述"
    )
    
    # 请求信息
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="HTTP请求方法"
    )
    
    request_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="请求路径"
    )
    
    request_params: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="请求参数"
    )
    
    # 客户端信息
    ip_address: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True,
        comment="IP地址"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User-Agent"
    )
    
    # 响应信息
    status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP状态码"
    )
    
    is_success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否成功"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="响应时间(毫秒)"
    )
    
    # 扩展数据
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="额外数据"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Asia/Shanghai")),
        index=True,
        comment="创建时间"
    )
    
    # 索引
    __table_args__ = (
        Index('ix_operation_logs_user_type_user_id', 'user_type', 'user_id'),
        Index('ix_operation_logs_user_type_created_at', 'user_type', 'created_at'),
        Index('ix_operation_logs_module_created_at', 'module', 'created_at'),
    )


# 用户类型枚举
class UserType:
    """用户类型"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


# 日志模块枚举（通用）
class LogModule:
    """日志模块"""
    # 通用模块
    AUTH = "auth"  # 认证
    
    # 管理端模块
    ADMIN = "admin"  # 管理员管理
    USER_MANAGE = "user_manage"  # 用户管理
    QUESTION = "question"  # 题目管理
    ANNOUNCEMENT = "announcement"  # 公告管理
    GRADE_KNOWLEDGE = "grade_knowledge"  # 年级知识点管理
    SYSTEM_CONFIG = "system_config"  # 系统配置
    SYSTEM = "system"  # 系统操作
    
    # 用户端模块
    PRACTICE = "practice"  # 练习
    WRONGBOOK = "wrongbook"  # 错题本
    ANALYSIS = "analysis"  # 学习分析
    
    # 其他
    OTHER = "other"  # 其他
