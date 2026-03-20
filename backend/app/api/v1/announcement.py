from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.repositories.announcement_repo import AnnouncementRepository
from app.schemas.announcement import AnnouncementPublicSchema


router = APIRouter(prefix="/announcements", tags=["公告"])


@router.get("/active", summary="用户端-获取当前有效公告")
async def list_active_announcements(
    limit: int = Query(default=10, ge=1, le=100, description="返回数量上限"),
    db: AsyncSession = Depends(get_db),
):
    repo = AnnouncementRepository(db)
    now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
    items = await repo.list_active(now=now, limit=limit)
    return success(data=[AnnouncementPublicSchema.model_validate(x).model_dump(mode="json") for x in items])
