from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.banner import (
    BannerCreateSchema,
    BannerListQuerySchema,
    BannerUpdateSchema,
)
from app.services.admin_banner_service import AdminBannerService

router = APIRouter(prefix="/admin/banners", tags=["管理端轮播图"])


@router.post(
    "/upload-image",
    summary="管理端-上传轮播图图片",
    dependencies=[Depends(session_security)],
)
async def upload_image(
    file: UploadFile = File(..., description="图片文件"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    data_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"
    result = await service.upload_image(data=data_bytes, content_type=content_type)
    return success(data=result.model_dump(), message="上传成功")


@router.get(
    "",
    summary="管理端-轮播图列表",
    dependencies=[Depends(session_security)],
)
async def list_banners(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    query = BannerListQuerySchema(
        page=page, page_size=page_size, is_active=is_active
    )
    items, total = await service.list(query)
    return page_success(
        data=[x.model_dump(mode="json") for x in items],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.post(
    "",
    summary="管理端-创建轮播图",
    dependencies=[Depends(session_security)],
)
async def create_banner(
    request: BannerCreateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    data = await service.create(admin_id=admin_id, data=request)
    return success(data=data.model_dump(mode="json"), message="创建成功")


@router.get(
    "/{banner_id}",
    summary="管理端-轮播图详情",
    dependencies=[Depends(session_security)],
)
async def get_banner(
    banner_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    data = await service.get(banner_id)
    return success(data=data.model_dump(mode="json"))


@router.put(
    "/{banner_id}",
    summary="管理端-更新轮播图",
    dependencies=[Depends(session_security)],
)
async def update_banner(
    banner_id: int,
    request: BannerUpdateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    data = await service.update(admin_id=admin_id, banner_id=banner_id, data=request)
    return success(data=data.model_dump(mode="json"), message="更新成功")


@router.patch(
    "/{banner_id}/active",
    summary="管理端-启用/停用轮播图",
    dependencies=[Depends(session_security)],
)
async def set_banner_active(
    banner_id: int,
    is_active: bool = Query(..., description="是否启用"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    data = await service.set_active(
        admin_id=admin_id, banner_id=banner_id, is_active=is_active
    )
    return success(data=data.model_dump(mode="json"), message="更新成功")


@router.delete(
    "/{banner_id}",
    summary="管理端-删除轮播图",
    dependencies=[Depends(session_security)],
)
async def delete_banner(
    banner_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminBannerService(db)
    await service.delete(banner_id)
    return success(message="删除成功")
