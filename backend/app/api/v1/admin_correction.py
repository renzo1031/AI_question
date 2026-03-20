"""
管理员纠错管理 API
"""
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.middleware.auth import get_current_admin_id
from app.schemas.correction import (
    QuestionCorrectionQuerySchema,
    QuestionCorrectionUpdateSchema,
)
from app.services.correction_service import CorrectionService

router = APIRouter(prefix="/admin/corrections", tags=["管理员-纠错管理"])


@router.get("", summary="查看所有纠错记录")
async def list_all_corrections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, regex="^(pending|resolved|ignored)$", description="状态筛选"),
    question_id: Optional[int] = Query(None, description="题目ID筛选"),
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    管理员查看所有纠错记录
    
    - 支持分页
    - 支持按状态筛选（pending/resolved/ignored）
    - 支持按题目ID筛选
    """
    service = CorrectionService(db)
    query = QuestionCorrectionQuerySchema(
        page=page,
        page_size=page_size,
        status=status,
        question_id=question_id
    )
    result = await service.list_corrections(query, admin_mode=True)
    return success(data=result)


@router.patch("/{correction_id}", summary="处理纠错记录")
async def handle_correction(
    correction_id: int = Path(..., description="纠错记录ID"),
    data: QuestionCorrectionUpdateSchema = ...,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    管理员处理纠错记录
    
    - **status**: resolved(已解决) / ignored(已忽略)
    - **admin_note**: 管理员备注（可选）
    """
    service = CorrectionService(db)
    result = await service.handle_correction(correction_id, data, admin_id)
    return success(data=result, message="处理成功")


@router.get("/stats", summary="获取纠错统计信息")
async def get_correction_stats(
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    获取纠错统计信息
    
    返回待处理纠错数量
    """
    service = CorrectionService(db)
    pending_count = await service.get_pending_count()
    return success(data={"pending_count": pending_count})
