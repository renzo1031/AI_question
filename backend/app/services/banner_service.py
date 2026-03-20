from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.banner_repo import BannerRepository
from app.schemas.banner import BannerPublicSchema


class BannerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = BannerRepository(db)

    async def list_active(self, limit: int = 20) -> list[BannerPublicSchema]:
        now = datetime.now(tz=timezone.utc)
        items = await self.repo.list_active(now=now, limit=limit)
        return [BannerPublicSchema.model_validate(x) for x in items]
