from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.services.admin_dashboard_service import AdminDashboardService


router = APIRouter(prefix="/admin/dashboard", tags=["管理端看板"])


@router.get("/overview", summary="管理端-看板概览", dependencies=[Depends(session_security)])
async def get_dashboard_overview(
    period: Literal["7d", "15d", "30d"] = Query(default="30d", description="统计周期：7d-最近7天, 15d-最近15天, 30d-最近30天"),
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取管理后台数据看板概览
    
    支持的时间周期：
    - 7d: 最近7天
    - 15d: 最近15天
    - 30d: 最近30天（默认）
    """
    # 将周期字符串转换为天数
    period_map = {
        "7d": 7,
        "15d": 15,
        "30d": 30
    }
    period_days = period_map[period]
    
    service = AdminDashboardService(db)
    data = await service.get_overview(period_days=period_days)
    return success(data=data.model_dump(mode="json"))
