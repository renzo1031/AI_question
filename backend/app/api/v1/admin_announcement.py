from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.announcement import (
    AnnouncementCreateSchema,
    AnnouncementListQuerySchema,
    AnnouncementUpdateSchema,
)
from app.services.admin_announcement_service import AdminAnnouncementService


router = APIRouter(prefix="/admin/announcements", tags=["管理端公告"])


@router.get("", summary="管理端-公告列表", dependencies=[Depends(session_security)])
async def list_announcements(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索（标题/内容）"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    query = AnnouncementListQuerySchema(page=page, page_size=page_size, keyword=keyword, is_active=is_active)
    items, total = await service.list(query)
    return page_success(
        data=[x.model_dump(mode="json") for x in items],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.get("/{announcement_id}", summary="管理端-公告详情", dependencies=[Depends(session_security)])
async def get_announcement(
    announcement_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    data = await service.get(announcement_id)
    return success(data=data.model_dump(mode="json"))


@router.post("", summary="管理端-创建公告", dependencies=[Depends(session_security)])
async def create_announcement(
    request: AnnouncementCreateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    data = await service.create(admin_id=admin_id, data=request)
    return success(data=data.model_dump(mode="json"), message="创建成功")


@router.put("/{announcement_id}", summary="管理端-更新公告", dependencies=[Depends(session_security)])
async def update_announcement(
    announcement_id: int,
    request: AnnouncementUpdateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    data = await service.update(admin_id=admin_id, announcement_id=announcement_id, data=request)
    return success(data=data.model_dump(mode="json"), message="更新成功")


@router.patch("/{announcement_id}/active", summary="管理端-启用/停用公告", dependencies=[Depends(session_security)])
async def set_announcement_active(
    announcement_id: int,
    is_active: bool = Query(..., description="是否启用"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    data = await service.set_active(admin_id=admin_id, announcement_id=announcement_id, is_active=is_active)
    return success(data=data.model_dump(mode="json"), message="更新成功")


@router.delete("/{announcement_id}", summary="管理端-删除公告", dependencies=[Depends(session_security)])
async def delete_announcement(
    announcement_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAnnouncementService(db)
    await service.delete(announcement_id)
    return success(message="删除成功")
