from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.announcement import Announcement


class AnnouncementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, announcement_id: int) -> Optional[Announcement]:
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        title: str,
        content: str,
        is_active: bool,
        start_at: Optional[datetime],
        end_at: Optional[datetime],
        sort_order: int,
        created_by_admin_id: Optional[str],
    ) -> Announcement:
        obj = Announcement(
            title=title,
            content=content,
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
        announcement_id: int,
        *,
        title: Optional[str] = None,
        content: Optional[str] = None,
        is_active: Optional[bool] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        sort_order: Optional[int] = None,
        updated_by_admin_id: Optional[str] = None,
    ) -> Optional[Announcement]:
        values = {}
        if title is not None:
            values["title"] = title
        if content is not None:
            values["content"] = content
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
                update(Announcement)
                .where(Announcement.id == announcement_id)
                .values(**values)
            )
            await self.db.flush()

        return await self.get_by_id(announcement_id)

    async def delete(self, announcement_id: int) -> bool:
        obj = await self.get_by_id(announcement_id)
        if not obj:
            return False
        await self.db.delete(obj)
        return True

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Announcement], int]:
        query = select(Announcement)
        count_query = select(func.count(Announcement.id))

        if keyword:
            cond = or_(
                Announcement.title.ilike(f"%{keyword}%"),
                Announcement.content.ilike(f"%{keyword}%"),
            )
            query = query.where(cond)
            count_query = count_query.where(cond)

        if is_active is not None:
            query = query.where(Announcement.is_active == is_active)
            count_query = count_query.where(Announcement.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Announcement.sort_order.desc(), Announcement.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_active(self, *, now: datetime, limit: int = 10) -> list[Announcement]:
        query = (
            select(Announcement)
            .where(
                Announcement.is_active.is_(True),
                and_(
                    or_(Announcement.start_at.is_(None), Announcement.start_at <= now),
                    or_(Announcement.end_at.is_(None), Announcement.end_at >= now),
                ),
            )
            .order_by(Announcement.sort_order.desc(), Announcement.id.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def expire_announcements(self, *, now: datetime) -> int:
        """
        禁用已过期的公告
        
        Args:
            now: 当前时间
            
        Returns:
            被禁用的公告数量
        """
        # 查找需要禁用的公告：is_active=True 且 end_at < now
        result = await self.db.execute(
            select(Announcement).where(
                Announcement.is_active.is_(True),
                Announcement.end_at.isnot(None),
                Announcement.end_at < now,
            )
        )
        expired_announcements = result.scalars().all()

        if expired_announcements:
            # 批量更新
            expired_ids = [ann.id for ann in expired_announcements]
            await self.db.execute(
                update(Announcement)
                .where(Announcement.id.in_(expired_ids))
                .values(is_active=False)
            )
            await self.db.flush()
            return len(expired_announcements)
        
        return 0
