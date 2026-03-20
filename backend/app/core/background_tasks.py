"""
后台任务模块
用于执行定期任务，如自动禁用过期公告、过期轮播图
"""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger
from sqlalchemy import select, update

from app.core.database import async_session_factory
from app.models.announcement import Announcement
from app.models.banner import Banner


class BackgroundTaskManager:
    """后台任务管理器"""

    def __init__(self):
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def start(self):
        """启动所有后台任务"""
        if self._running:
            logger.warning("Background tasks already running")
            return

        self._running = True
        logger.info("Starting background tasks...")

        # 启动各个定期任务
        self._tasks.append(asyncio.create_task(self._expire_announcements_task()))
        self._tasks.append(asyncio.create_task(self._expire_banners_task()))

        logger.info(f"Started {len(self._tasks)} background tasks")

    async def stop(self):
        """停止所有后台任务"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping background tasks...")

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        # 等待所有任务完成
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        logger.info("All background tasks stopped")

    async def _expire_announcements_task(self):
        """定期检查并禁用过期公告的任务"""
        check_interval = 60  # 每60秒检查一次

        logger.info(f"Announcement expiration task started (interval: {check_interval}s)")

        while self._running:
            try:
                await self._expire_announcements()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                logger.info("Announcement expiration task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in announcement expiration task: {e}")
                # 出错后等待一段时间再继续
                await asyncio.sleep(check_interval)

    async def _expire_announcements(self):
        """禁用已过期的公告"""
        try:
            async with async_session_factory() as db:
                now = datetime.now(ZoneInfo("Asia/Shanghai"))

                # 查找需要禁用的公告：is_active=True 且 end_at < now
                result = await db.execute(
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
                    await db.execute(
                        update(Announcement)
                        .where(Announcement.id.in_(expired_ids))
                        .values(is_active=False)
                    )
                    await db.commit()

                    logger.info(
                        f"Disabled {len(expired_announcements)} expired announcement(s): "
                        f"{[ann.id for ann in expired_announcements]}"
                    )

        except Exception as e:
            logger.error(f"Failed to expire announcements: {e}")
            raise

    async def _expire_banners_task(self):
        """定期检查并禁用过期轮播图的任务"""
        check_interval = 60  # 每60秒检查一次

        logger.info(f"Banner expiration task started (interval: {check_interval}s)")

        while self._running:
            try:
                await self._expire_banners()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                logger.info("Banner expiration task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in banner expiration task: {e}")
                await asyncio.sleep(check_interval)

    async def _expire_banners(self):
        """禁用已超过 end_at 的轮播图"""
        try:
            async with async_session_factory() as db:
                now = datetime.now(ZoneInfo("Asia/Shanghai"))

                result = await db.execute(
                    select(Banner).where(
                        Banner.is_active.is_(True),
                        Banner.end_at.isnot(None),
                        Banner.end_at < now,
                    )
                )
                expired_banners = result.scalars().all()

                if expired_banners:
                    expired_ids = [b.id for b in expired_banners]
                    await db.execute(
                        update(Banner)
                        .where(Banner.id.in_(expired_ids))
                        .values(is_active=False)
                    )
                    await db.commit()

                    logger.info(
                        f"Disabled {len(expired_banners)} expired banner(s): "
                        f"{expired_ids}"
                    )

        except Exception as e:
            logger.error(f"Failed to expire banners: {e}")
            raise


# 全局实例
background_task_manager = BackgroundTaskManager()
