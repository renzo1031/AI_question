from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banner import Banner


class BannerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, banner_id: int) -> Optional[Banner]:
        result = await self.db.execute(select(Banner).where(Banner.id == banner_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        image_url: str,
        image_key: str,
        link_url: Optional[str],
        link_type: str,
        is_active: bool,
        start_at: Optional[datetime],
        end_at: Optional[datetime],
        sort_order: int,
        created_by_admin_id: Optional[str],
    ) -> Banner:
        obj = Banner(
            image_url=image_url,
            image_key=image_key,
            link_url=link_url,
            link_type=link_type,
            is_active=is_active,
            start_at=start_at,
            end_at=end_at,
            sort_order=sort_order,
            created_by_admin_id=created_by_admin_id,
            updated_by_admin_id=created_by_admin_id,
        )
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(
        self,
        banner_id: int,
        *,
        image_url: Optional[str] = None,
        image_key: Optional[str] = None,
        link_url: Optional[str] = None,
        link_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        sort_order: Optional[int] = None,
        updated_by_admin_id: Optional[str] = None,
    ) -> Optional[Banner]:
        values: dict = {}
        if image_url is not None:
            values["image_url"] = image_url
        if image_key is not None:
            values["image_key"] = image_key
        if link_url is not None:
            values["link_url"] = link_url
        if link_type is not None:
            values["link_type"] = link_type
        if is_active is not None:
            values["is_active"] = is_active
        if start_at is not None:
            values["start_at"] = start_at
        if end_at is not None:
            values["end_at"] = end_at
        if sort_order is not None:
            values["sort_order"] = sort_order
        if updated_by_admin_id is not None:
            values["updated_by_admin_id"] = updated_by_admin_id

        if values:
            await self.db.execute(
                update(Banner).where(Banner.id == banner_id).values(**values)
            )
            await self.db.flush()

        return await self.get_by_id(banner_id)

    async def delete(self, banner_id: int) -> bool:
        obj = await self.get_by_id(banner_id)
        if not obj:
            return False
        await self.db.delete(obj)
        return True

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Banner], int]:
        query = select(Banner)
        count_query = select(func.count(Banner.id))

        if is_active is not None:
            query = query.where(Banner.is_active == is_active)
            count_query = count_query.where(Banner.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Banner.sort_order.desc(), Banner.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_active(self, *, now: datetime, limit: int = 20) -> list[Banner]:
        """返回当前有效的轮播图列表（is_active=True 且在生效时间窗口内）"""
        query = (
            select(Banner)
            .where(
                Banner.is_active.is_(True),
                and_(
                    or_(Banner.start_at.is_(None), Banner.start_at <= now),
                    or_(Banner.end_at.is_(None), Banner.end_at >= now),
                ),
            )
            .order_by(Banner.sort_order.desc(), Banner.id.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
