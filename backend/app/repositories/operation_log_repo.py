"""操作日志数据访问层"""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogListRequest


class OperationLogRepository:
    """操作日志仓储"""
    
    @staticmethod
    async def create(db: AsyncSession, log_data: dict) -> OperationLog:
        """创建操作日志"""
        log = OperationLog(**log_data)
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[OperationLog]:
        """根据ID获取日志"""
        stmt = select(OperationLog).where(OperationLog.id == log_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        request: OperationLogListRequest,
    ) -> tuple[list[OperationLog], int]:
        """
        获取日志列表（分页）
        
        返回: (日志列表, 总数)
        """
        # 构建查询条件
        conditions = []
        
        if request.user_type:
            conditions.append(OperationLog.user_type == request.user_type)
        
        if request.user_id:
            conditions.append(OperationLog.user_id == request.user_id)
        
        if request.username:
            conditions.append(OperationLog.username.ilike(f"%{request.username}%"))
        
        if request.log_level:
            conditions.append(OperationLog.log_level == request.log_level)
        
        if request.module:
            conditions.append(OperationLog.module == request.module)
        
        if request.action:
            conditions.append(OperationLog.action.ilike(f"%{request.action}%"))
        
        if request.is_success is not None:
            conditions.append(OperationLog.is_success == request.is_success)
        
        if request.start_time:
            conditions.append(OperationLog.created_at >= request.start_time)
        
        if request.end_time:
            conditions.append(OperationLog.created_at <= request.end_time)
        
        # 构建查询
        query = select(OperationLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(OperationLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.order_by(OperationLog.created_at.desc())
        query = query.offset((request.page - 1) * request.page_size)
        query = query.limit(request.page_size)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total
    
    @staticmethod
    async def get_stats(
        db: AsyncSession,
        user_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> dict:
        """
        获取日志统计信息
        
        返回：
        {
            "total": 总日志数,
            "by_user_type": {用户类型: 数量},
            "by_module": {模块: 数量},
            "by_log_level": {日志级别: 数量},
            "success_count": 成功数,
            "failure_count": 失败数,
        }
        """
        # 构建基础条件
        conditions = []
        if user_type:
            conditions.append(OperationLog.user_type == user_type)
        if start_time:
            conditions.append(OperationLog.created_at >= start_time)
        if end_time:
            conditions.append(OperationLog.created_at <= end_time)
        
        base_query = select(OperationLog)
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # 总数
        count_query = select(func.count()).select_from(OperationLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 按用户类型统计
        type_query = (
            select(
                OperationLog.user_type,
                func.count(OperationLog.id).label("count")
            )
            .group_by(OperationLog.user_type)
        )
        if conditions:
            type_query = type_query.where(and_(*conditions))
        result = await db.execute(type_query)
        by_user_type = {row[0]: row[1] for row in result.all()}
        
        # 按模块统计
        module_query = (
            select(
                OperationLog.module,
                func.count(OperationLog.id).label("count")
            )
            .group_by(OperationLog.module)
            .order_by(func.count(OperationLog.id).desc())
            .limit(10)  # 只返回前10个
        )
        if conditions:
            module_query = module_query.where(and_(*conditions))
        result = await db.execute(module_query)
        by_module = {row[0]: row[1] for row in result.all()}
        
        # 按日志级别统计
        level_query = (
            select(
                OperationLog.log_level,
                func.count(OperationLog.id).label("count")
            )
            .group_by(OperationLog.log_level)
        )
        if conditions:
            level_query = level_query.where(and_(*conditions))
        result = await db.execute(level_query)
        by_log_level = {row[0]: row[1] for row in result.all()}
        
        # 成功/失败统计
        success_query = (
            select(func.count())
            .select_from(OperationLog)
            .where(OperationLog.is_success == True)
        )
        if conditions:
            success_query = success_query.where(and_(*conditions))
        result = await db.execute(success_query)
        success_count = result.scalar()
        
        failure_count = total - success_count
        
        return {
            "total": total,
            "by_user_type": by_user_type,
            "by_module": by_module,
            "by_log_level": by_log_level,
            "success_count": success_count,
            "failure_count": failure_count,
        }
    
    @staticmethod
    async def delete_logs_before(
        db: AsyncSession,
        before_date: datetime,
    ) -> int:
        """
        删除指定日期之前的日志
        
        Args:
            db: 数据库会话
            before_date: 删除此日期之前的日志
            
        Returns:
            删除的日志数量
        """
        from sqlalchemy import delete
        
        stmt = delete(OperationLog).where(
            OperationLog.created_at < before_date
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        return result.rowcount
