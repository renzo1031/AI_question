"""系统配置 Repository"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_config import SystemConfig


class SystemConfigRepository:
    """系统配置仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """根据配置键获取配置"""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        return result.scalar_one_or_none()

    async def get_by_group(self, config_group: str) -> list[SystemConfig]:
        """获取指定分组的所有配置"""
        result = await self.db.execute(
            select(SystemConfig)
            .where(SystemConfig.config_group == config_group)
            .order_by(SystemConfig.config_key)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[SystemConfig]:
        """获取所有配置"""
        result = await self.db.execute(
            select(SystemConfig).order_by(SystemConfig.config_group, SystemConfig.config_key)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        config_key: str,
        config_group: str,
        config_name: str,
        config_value: str,
        description: Optional[str] = None,
        is_encrypted: bool = False,
        is_enabled: bool = True,
        created_by_admin_id: Optional[str] = None,
    ) -> SystemConfig:
        """创建配置"""
        config = SystemConfig(
            config_key=config_key,
            config_group=config_group,
            config_name=config_name,
            config_value=config_value,
            description=description,
            is_encrypted=is_encrypted,
            is_enabled=is_enabled,
            created_by_admin_id=created_by_admin_id,
            updated_by_admin_id=created_by_admin_id,
        )
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def update(
        self,
        config_key: str,
        *,
        config_value: Optional[str] = None,
        config_name: Optional[str] = None,
        description: Optional[str] = None,
        is_encrypted: Optional[bool] = None,
        is_enabled: Optional[bool] = None,
        updated_by_admin_id: Optional[str] = None,
    ) -> Optional[SystemConfig]:
        """更新配置"""
        config = await self.get_by_key(config_key)
        if not config:
            return None

        if config_value is not None:
            config.config_value = config_value
        if config_name is not None:
            config.config_name = config_name
        if description is not None:
            config.description = description
        if is_encrypted is not None:
            config.is_encrypted = is_encrypted
        if is_enabled is not None:
            config.is_enabled = is_enabled
        if updated_by_admin_id is not None:
            config.updated_by_admin_id = updated_by_admin_id

        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def delete(self, config_key: str) -> bool:
        """删除配置"""
        config = await self.get_by_key(config_key)
        if not config:
            return False
        
        await self.db.delete(config)
        await self.db.flush()
        return True

    async def upsert(
        self,
        *,
        config_key: str,
        config_group: str,
        config_name: str,
        config_value: str,
        description: Optional[str] = None,
        is_encrypted: bool = False,
        is_enabled: bool = True,
        admin_id: Optional[str] = None,
    ) -> SystemConfig:
        """创建或更新配置"""
        existing = await self.get_by_key(config_key)
        
        if existing:
            return await self.update(
                config_key,
                config_value=config_value,
                config_name=config_name,
                description=description,
                is_encrypted=is_encrypted,
                is_enabled=is_enabled,
                updated_by_admin_id=admin_id,
            )
        else:
            return await self.create(
                config_key=config_key,
                config_group=config_group,
                config_name=config_name,
                config_value=config_value,
                description=description,
                is_encrypted=is_encrypted,
                is_enabled=is_enabled,
                created_by_admin_id=admin_id,
            )
