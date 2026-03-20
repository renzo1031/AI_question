from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.repositories.announcement_repo import AnnouncementRepository
from app.schemas.announcement import (
    AnnouncementCreateSchema,
    AnnouncementListQuerySchema,
    AnnouncementResponseSchema,
    AnnouncementUpdateSchema,
)


class AdminAnnouncementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AnnouncementRepository(db)

    @staticmethod
    def _validate_time_window(start_at: Optional[datetime], end_at: Optional[datetime]) -> None:
        if start_at and end_at and start_at > end_at:
            raise AppException(code=ErrorCode.PARAM_ERROR, message="start_at 不能晚于 end_at")

    async def list(self, query: AnnouncementListQuerySchema):
        items, total = await self.repo.list(
            page=query.page,
            page_size=query.page_size,
            keyword=query.keyword,
            is_active=query.is_active,
        )
        return [AnnouncementResponseSchema.model_validate(x) for x in items], total

    async def get(self, announcement_id: int) -> AnnouncementResponseSchema:
        obj = await self.repo.get_by_id(announcement_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="公告不存在")
        return AnnouncementResponseSchema.model_validate(obj)

    async def create(self, admin_id: str, data: AnnouncementCreateSchema) -> AnnouncementResponseSchema:
        self._validate_time_window(data.start_at, data.end_at)
        obj = await self.repo.create(
            title=data.title,
            content=data.content,
            is_active=data.is_active,
            start_at=data.start_at,
            end_at=data.end_at,
            sort_order=data.sort_order,
            created_by_admin_id=admin_id,
        )
        await self.db.commit()
        return AnnouncementResponseSchema.model_validate(obj)

    async def update(self, admin_id: str, announcement_id: int, data: AnnouncementUpdateSchema) -> AnnouncementResponseSchema:
        current = await self.repo.get_by_id(announcement_id)
        if not current:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="公告不存在")

        start_at = data.start_at if data.start_at is not None else current.start_at
        end_at = data.end_at if data.end_at is not None else current.end_at
        self._validate_time_window(start_at, end_at)

        updated = await self.repo.update(
            announcement_id,
            title=data.title,
            content=data.content,
            is_active=data.is_active,
            start_at=data.start_at,
            end_at=data.end_at,
            sort_order=data.sort_order,
            updated_by_admin_id=admin_id,
        )
        await self.db.commit()
        return AnnouncementResponseSchema.model_validate(updated)

    async def set_active(self, admin_id: str, announcement_id: int, is_active: bool) -> AnnouncementResponseSchema:
        obj = await self.repo.get_by_id(announcement_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="公告不存在")

        updated = await self.repo.update(
            announcement_id,
            is_active=is_active,
            updated_by_admin_id=admin_id,
        )
        await self.db.commit()
        return AnnouncementResponseSchema.model_validate(updated)

    async def delete(self, announcement_id: int) -> bool:
        obj = await self.repo.get_by_id(announcement_id)
        if not obj:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="公告不存在")

        ok = await self.repo.delete(announcement_id)
        await self.db.commit()
        return ok
