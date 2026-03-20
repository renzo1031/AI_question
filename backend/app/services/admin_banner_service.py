from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.core.minio_client import minio_client
from app.repositories.banner_repo import BannerRepository
from app.schemas.banner import (
    BannerCreateSchema,
    BannerListQuerySchema,
    BannerResponseSchema,
    BannerUpdateSchema,
    BannerUploadResponseSchema,
)


class AdminBannerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = BannerRepository(db)

    @staticmethod
    def _validate_time_window(
        start_at: Optional[datetime], end_at: Optional[datetime]
    ) -> None:
        if start_at and end_at and start_at > end_at:
            raise AppException(code=ErrorCode.PARAM_ERROR, message="start_at 不能晚于 end_at")

    async def upload_image(
        self, data: bytes, content_type: str
    ) -> BannerUploadResponseSchema:
        """上传图片到 MinIO，返回 image_key 和 image_url"""
        object_key, public_url = await minio_client.upload_file(
            data=data, content_type=content_type
        )
        return BannerUploadResponseSchema(image_url=public_url, image_key=object_key)

    async def list(
        self, query: BannerListQuerySchema
    ) -> tuple[list[BannerResponseSchema], int]:
        items, total = await self.repo.list(
            page=query.page,
            page_size=query.page_size,
            is_active=query.is_active,
        )
        return [BannerResponseSchema.model_validate(x) for x in items], total

    async def get(self, banner_id: int) -> BannerResponseSchema:
        obj = await self.repo.get_by_id(banner_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="轮播图不存在")
        return BannerResponseSchema.model_validate(obj)

    async def create(
        self, admin_id: str, data: BannerCreateSchema
    ) -> BannerResponseSchema:
        self._validate_time_window(data.start_at, data.end_at)
        obj = await self.repo.create(
            image_url=data.image_url,
            image_key=data.image_key,
            link_url=data.link_url,
            link_type=data.link_type,
            is_active=data.is_active,
            start_at=data.start_at,
            end_at=data.end_at,
            sort_order=data.sort_order,
            created_by_admin_id=admin_id,
        )
        await self.db.commit()
        return BannerResponseSchema.model_validate(obj)

    async def update(
        self, admin_id: str, banner_id: int, data: BannerUpdateSchema
    ) -> BannerResponseSchema:
        current = await self.repo.get_by_id(banner_id)
        if not current:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="轮播图不存在")

        start_at = data.start_at if data.start_at is not None else current.start_at
        end_at = data.end_at if data.end_at is not None else current.end_at
        self._validate_time_window(start_at, end_at)

        old_image_key: Optional[str] = None
        if data.image_key is not None and data.image_key != current.image_key:
            old_image_key = current.image_key

        updated = await self.repo.update(
            banner_id,
            image_url=data.image_url,
            image_key=data.image_key,
            link_url=data.link_url,
            link_type=data.link_type,
            is_active=data.is_active,
            start_at=data.start_at,
            end_at=data.end_at,
            sort_order=data.sort_order,
            updated_by_admin_id=admin_id,
        )
        await self.db.commit()

        if old_image_key:
            await minio_client.delete_file(old_image_key)

        return BannerResponseSchema.model_validate(updated)

    async def set_active(
        self, admin_id: str, banner_id: int, is_active: bool
    ) -> BannerResponseSchema:
        obj = await self.repo.get_by_id(banner_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="轮播图不存在")
        updated = await self.repo.update(
            banner_id, is_active=is_active, updated_by_admin_id=admin_id
        )
        await self.db.commit()
        return BannerResponseSchema.model_validate(updated)

    async def delete(self, banner_id: int) -> None:
        obj = await self.repo.get_by_id(banner_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="轮播图不存在")
        image_key = obj.image_key
        await self.repo.delete(banner_id)
        await self.db.commit()
        await minio_client.delete_file(image_key)
