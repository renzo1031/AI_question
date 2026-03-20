"""操作日志服务层"""
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from app.common.exceptions import AppException
from app.core.database import get_db
from app.repositories.operation_log_repo import OperationLogRepository
from app.schemas.operation_log import (
    OperationLogListRequest,
    OperationLogListResponse,
    OperationLogResponse,
)


class OperationLogService:
    """操作日志服务"""
    
    @staticmethod
    async def get_logs(
        request: OperationLogListRequest,
    ) -> OperationLogListResponse:
        """获取日志列表"""
        async for db in get_db():
            logs, total = await OperationLogRepository.get_logs(db, request)
            
            return OperationLogListResponse(
                total=total,
                page=request.page,
                page_size=request.page_size,
                items=[OperationLogResponse.model_validate(log) for log in logs],
            )
    
    @staticmethod
    async def get_log_by_id(log_id: int) -> OperationLogResponse:
        """获取日志详情"""
        async for db in get_db():
            log = await OperationLogRepository.get_by_id(db, log_id)
            
            if not log:
                raise AppException(message="日志不存在", code=404)
            
            return OperationLogResponse.model_validate(log)
    
    @staticmethod
    async def get_log_stats(
        user_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> dict:
        """获取日志统计信息"""
        async for db in get_db():
            stats = await OperationLogRepository.get_stats(
                db,
                user_type=user_type,
                start_time=start_time,
                end_time=end_time,
            )
            
            return stats
    
    @staticmethod
    async def cleanup_old_logs(days: int = 30) -> dict:
        """
        清理旧日志
        
        Args:
            days: 保留最近多少天的日志，默认30天
            
        Returns:
            {"deleted_count": 删除数量, "before_date": 删除日期}
        """
        from datetime import timedelta
        
        before_date = datetime.now(ZoneInfo("Asia/Shanghai")) - timedelta(days=days)
        
        async for db in get_db():
            deleted_count = await OperationLogRepository.delete_logs_before(
                db,
                before_date=before_date
            )
            
            return {
                "deleted_count": deleted_count,
                "before_date": before_date.isoformat(),
                "days": days,
            }
