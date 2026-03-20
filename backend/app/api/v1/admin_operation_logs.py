"""
管理端操作日志API
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from loguru import logger

from app.common.response import ResponseModel, success
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.operation_log import (
    OperationLogListRequest,
    OperationLogListResponse,
    OperationLogResponse,
)
from app.services.operation_log import OperationLogService

router = APIRouter(prefix="/operation-logs", tags=["管理端-操作日志"])


@router.get("", summary="获取日志列表",response_model=ResponseModel[OperationLogListResponse], dependencies=[Depends(session_security)])
async def get_operation_logs(
    user_type: Optional[str] = Query(None, description="用户类型：admin/user，不传则查询全部"),
    user_id: Optional[UUID] = Query(None, description="用户ID"),
    username: Optional[str] = Query(None, description="用户名（管理员用户名或用户手机号）"),
    log_level: Optional[str] = Query(None, description="日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL"),
    module: Optional[str] = Query(None, description="所属模块"),
    action: Optional[str] = Query(None, description="操作动作（模糊搜索）"),
    is_success: Optional[bool] = Query(None, description="是否成功"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    admin_id: str = Depends(get_current_admin_id),
):
    """
    获取操作日志列表
    
    支持多种筛选条件：
    - user_type: 按用户类型筛选（admin/user）
    - user_id: 按用户ID筛选
    - username: 按用户名筛选
    - log_level: 按日志级别筛选
    - module: 按模块筛选
    - action: 按操作动作模糊搜索
    - is_success: 按成功状态筛选
    - start_time/end_time: 按时间范围筛选
    """
    logger.info(
        f"管理员 {admin_id} 查询操作日志: "
        f"user_type={user_type}, module={module}, page={page}"
    )
    
    request = OperationLogListRequest(
        user_type=user_type,
        user_id=user_id,
        username=username,
        log_level=log_level,
        module=module,
        action=action,
        is_success=is_success,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )
    
    result = await OperationLogService.get_logs(request)
    return success(data=result)


@router.get("/{log_id}", summary="获取日志详细",response_model=ResponseModel[OperationLogResponse], dependencies=[Depends(session_security)])
async def get_operation_log_detail(
    log_id: int,
    admin_id: str = Depends(get_current_admin_id),
):
    """获取操作日志详情"""
    logger.info(f"管理员 {admin_id} 查询操作日志详情: log_id={log_id}")
    
    log = await OperationLogService.get_log_by_id(log_id)
    return success(data=log)


@router.get("/stats/summary", summary="获取日志统计",response_model=ResponseModel[dict], dependencies=[Depends(session_security)])
async def get_operation_log_stats(
    user_type: Optional[str] = Query(None, description="用户类型：admin/user"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    admin_id: str = Depends(get_current_admin_id),
):
    """
    获取操作日志统计信息
    
    返回：
    - 总日志数
    - 各用户类型日志数
    - 各模块日志数
    - 各日志级别日志数
    - 成功/失败统计
    """
    logger.info(
        f"管理员 {admin_id} 查询操作日志统计: "
        f"user_type={user_type}, start_time={start_time}, end_time={end_time}"
    )
    
    stats = await OperationLogService.get_log_stats(
        user_type=user_type,
        start_time=start_time,
        end_time=end_time,
    )
    return success(data=stats)


@router.delete("/cleanup",summary="清理旧日志", response_model=ResponseModel[dict], dependencies=[Depends(session_security)])
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留最近多少天的日志"),
    admin_id: str = Depends(get_current_admin_id),
):
    """
    清理旧日志
    
    删除指定天数之前的所有日志。
    
    Args:
        days: 保留最近多少天的日志，默认30天，范围 1-365 天
    
    Returns:
        {
            "deleted_count": 删除的日志数量,
            "before_date": 删除的截止日期,
            "days": 保留天数
        }
    """
    logger.warning(
        f"管理员 {admin_id} 执行日志清理: 保留最近 {days} 天"
    )
    
    result = await OperationLogService.cleanup_old_logs(days=days)
    
    logger.info(
        f"日志清理完成: 删除 {result['deleted_count']} 条日志"
    )
    
    return success(data=result, message=f"成功清理 {result['deleted_count']} 条旧日志")
