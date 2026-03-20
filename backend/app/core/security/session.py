"""
Session管理模块
用于管理员用户的Session Cookie认证
"""
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security.sm4 import sm4_cipher


class SessionManager:
    """Session管理类"""
    
    SESSION_PREFIX = "admin_session:"
    
    def __init__(self):
        self.expire_hours = settings.session_expire_hours
    
    def _generate_session_id(self) -> str:
        """生成随机Session ID"""
        return secrets.token_urlsafe(32)
    
    async def create_session(self, admin_id: int, data: Optional[dict] = None) -> str:
        """
        创建管理员Session
        
        Args:
            admin_id: 管理员ID
            data: 额外的Session数据
            
        Returns:
            SM4加密后的Session ID（用于Cookie）
        """
        session_id = self._generate_session_id()
        session_data = {
            "admin_id": admin_id,
            "created_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            "expires_at": (
                datetime.now(ZoneInfo("Asia/Shanghai")) + timedelta(hours=self.expire_hours)
            ).isoformat(),
            **(data or {})
        }
        
        # 存储到Redis
        expire_seconds = self.expire_hours * 3600
        await redis_client.set_json(
            f"{self.SESSION_PREFIX}{session_id}",
            session_data,
            expire_seconds
        )
        
        # 返回加密的Session ID
        return sm4_cipher.encrypt(session_id)
    
    async def get_session(self, encrypted_session_id: str) -> Optional[dict[str, Any]]:
        """
        获取Session数据
        
        Args:
            encrypted_session_id: SM4加密的Session ID
            
        Returns:
            Session数据，不存在或过期返回None
        """
        try:
            session_id = sm4_cipher.decrypt(encrypted_session_id)
            return await redis_client.get_json(f"{self.SESSION_PREFIX}{session_id}")
        except Exception:
            return None
    
    async def refresh_session(self, encrypted_session_id: str) -> bool:
        """
        刷新Session过期时间
        
        Args:
            encrypted_session_id: SM4加密的Session ID
            
        Returns:
            是否刷新成功
        """
        try:
            session_id = sm4_cipher.decrypt(encrypted_session_id)
            key = f"{self.SESSION_PREFIX}{session_id}"
            
            # 获取现有Session
            session_data = await redis_client.get_json(key)
            if not session_data:
                return False
            
            # 更新过期时间
            session_data["expires_at"] = (
                datetime.now(ZoneInfo("Asia/Shanghai")) + timedelta(hours=self.expire_hours)
            ).isoformat()
            
            expire_seconds = self.expire_hours * 3600
            await redis_client.set_json(key, session_data, expire_seconds)
            return True
        except Exception:
            return False
    
    async def destroy_session(self, encrypted_session_id: str) -> bool:
        """
        销毁Session
        
        Args:
            encrypted_session_id: SM4加密的Session ID
            
        Returns:
            是否销毁成功
        """
        try:
            session_id = sm4_cipher.decrypt(encrypted_session_id)
            result = await redis_client.delete(f"{self.SESSION_PREFIX}{session_id}")
            return result > 0
        except Exception:
            return False
    
    async def get_admin_id(self, encrypted_session_id: str) -> Optional[int]:
        """
        从Session获取管理员ID
        
        Args:
            encrypted_session_id: SM4加密的Session ID
            
        Returns:
            管理员ID，Session无效返回None
        """
        session_data = await self.get_session(encrypted_session_id)
        if session_data:
            return session_data.get("admin_id")
        return None


# 全局Session管理器实例
session_manager = SessionManager()

