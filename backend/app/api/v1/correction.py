"""
用户端纠错 API
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.middleware.auth import get_current_user_id_optional
from app.schemas.correction import (
    QuestionCorrectionCreateSchema,
    QuestionCorrectionQuerySchema,
)
from app.services.correction_service import CorrectionService

router = APIRouter(prefix="/corrections", tags=["纠错管理"])


@router.post("", summary="提交纠错")
async def submit_correction(
    data: QuestionCorrectionCreateSchema,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """
    用户提交题目纠错（支持匿名提交）
    
    - **question_id**: 题目ID
    - **reason**: 纠错原因（可选）
    """
    service = CorrectionService(db)
    result = await service.submit_correction(data, user_id=user_id)
    return success(data=result)


@router.get("/my", summary="查看我的纠错记录")
async def get_my_corrections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, regex="^(pending|resolved|ignored)$", description="状态筛选"),
    question_id: Optional[int] = Query(None, description="题目ID筛选"),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """
    查看当前用户的纠错记录列表
    
    - 支持分页
    - 支持按状态筛选
    - 支持按题目ID筛选
    """
    if not user_id:
        # 匿名用户无法查看记录
        return success(data={
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        })
    
    service = CorrectionService(db)
    query = QuestionCorrectionQuerySchema(
        page=page,
        page_size=page_size,
        status=status,
        question_id=question_id
    )
    result = await service.list_corrections(
        query, 
        user_id=user_id, 
        admin_mode=False
    )
    return success(data=result)
