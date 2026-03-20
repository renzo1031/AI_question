from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.services.banner_service import BannerService

router = APIRouter(prefix="/banners", tags=["轮播图"])


@router.get("/active", summary="首页-获取当前有效轮播图列表")
async def list_active_banners(
    db: AsyncSession = Depends(get_db),
):
    service = BannerService(db)
    items = await service.list_active()
    return success(data=[x.model_dump(mode="json") for x in items])
