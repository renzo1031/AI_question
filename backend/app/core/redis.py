"""
Redis连接模块
提供异步Redis连接和常用操作
"""
import json
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


class RedisClient:
    """Redis客户端封装"""
    
    _instance: Optional["RedisClient"] = None
    _client: Optional[Redis] = None
    
    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """建立Redis连接"""
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    
    async def ping(self) -> bool:
        """
        检测Redis连接是否正常
        
        Returns:
            True表示连接正常，False表示连接异常
        """
        try:
            if self._client is None:
                return False
            result = await self._client.ping()
            return result is True
        except Exception:
            return False
    
    async def check_connection(self) -> tuple[bool, str]:
        """
        检查Redis连接状态
        
        Returns:
            (是否连接成功, 错误信息)
        """
        try:
            if self._client is None:
                await self.connect()
            
            # 执行 PING 命令检测连接
            result = await self._client.ping()
            if result:
                return True, "Redis连接正常"
            else:
                return False, "Redis PING 返回异常"
        except redis.ConnectionError as e:
            return False, f"Redis连接失败: {str(e)}"
        except redis.TimeoutError as e:
            return False, f"Redis连接超时: {str(e)}"
        except Exception as e:
            return False, f"Redis连接异常: {str(e)}"
    
    async def disconnect(self) -> None:
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def client(self) -> Redis:
        """获取Redis客户端"""
        if self._client is None:
            raise RuntimeError("Redis client not connected")
        return self._client
    
    # ==================== 基础操作 ====================
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        return await self.client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        设置值
        
        Args:
            key: 键名
            value: 值
            expire: 过期时间（秒）
            nx: 只在键不存在时设置（用于分布式锁）
            
        Returns:
            是否设置成功
        """
        if nx:
            return await self.client.set(key, value, nx=True, ex=expire)
        else:
            return await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """删除键"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.client.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return await self.client.ttl(key)
    
    # ==================== JSON操作 ====================
    
    async def get_json(self, key: str) -> Optional[Any]:
        """获取JSON值"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """设置JSON值"""
        return await self.set(key, json.dumps(value, ensure_ascii=False), expire)
    
    # ==================== 验证码相关 ====================
    
    async def set_verify_code(
        self, 
        key: str, 
        code: str, 
        expire: int = 300
    ) -> bool:
        """设置验证码（默认5分钟过期）"""
        return await self.set(f"verify_code:{key}", code, expire)
    
    async def get_verify_code(self, key: str) -> Optional[str]:
        """获取验证码"""
        return await self.get(f"verify_code:{key}")
    
    async def delete_verify_code(self, key: str) -> int:
        """删除验证码"""
        return await self.delete(f"verify_code:{key}")
    
    # ==================== Session相关 ====================
    
    async def set_session(
        self, 
        session_id: str, 
        data: dict, 
        expire: int = 86400
    ) -> bool:
        """设置Session数据"""
        return await self.set_json(f"session:{session_id}", data, expire)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取Session数据"""
        return await self.get_json(f"session:{session_id}")
    
    async def delete_session(self, session_id: str) -> int:
        """删除Session"""
        return await self.delete(f"session:{session_id}")
    
    # ==================== Token黑名单 ====================
    
    async def add_token_blacklist(
        self, 
        token: str, 
        expire: int = 86400
    ) -> bool:
        """将Token加入黑名单"""
        return await self.set(f"token_blacklist:{token}", "1", expire)
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """检查Token是否在黑名单中"""
        return await self.exists(f"token_blacklist:{token}")
    
    # ==================== 分布式锁相关 ====================
    
    async def acquire_lock(
        self,
        key: str,
        timeout: int = 60,
        blocking_timeout: float = 5.0
    ) -> Optional[str]:
        """
        获取分布式锁
        
        使用 Redis SET NX EX 命令实现分布式锁
        
        Args:
            key: 锁的键名
            timeout: 锁的过期时间（秒），默认60秒
            blocking_timeout: 阻塞等待时间（秒），如果为0则不阻塞，默认5秒
            
        Returns:
            锁的标识符（用于释放锁），如果获取失败返回None
        """
        import uuid
        lock_identifier = str(uuid.uuid4())
        lock_key = f"lock:{key}"
        
        # 尝试获取锁
        result = await self.client.set(
            lock_key,
            lock_identifier,
            nx=True,  # 只在键不存在时设置
            ex=timeout  # 设置过期时间
        )
        
        if result:
            return lock_identifier
        
        # 如果设置了阻塞等待时间，则等待一段时间后重试
        if blocking_timeout > 0:
            import asyncio
            elapsed = 0.0
            while elapsed < blocking_timeout:
                await asyncio.sleep(0.1)  # 等待100ms后重试
                elapsed += 0.1
                result = await self.client.set(
                    lock_key,
                    lock_identifier,
                    nx=True,
                    ex=timeout
                )
                if result:
                    return lock_identifier
        
        return None
    
    async def release_lock(self, key: str, lock_identifier: str) -> bool:
        """
        释放分布式锁
        
        使用 Lua 脚本确保原子性：只有锁的标识符匹配时才删除
        
        Args:
            key: 锁的键名
            lock_identifier: 锁的标识符（获取锁时返回的值）
            
        Returns:
            是否成功释放锁
        """
        lock_key = f"lock:{key}"
        
        # 使用 Lua 脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            result = await self.client.eval(lua_script, 1, lock_key, lock_identifier)
            return result == 1
        except Exception:
            return False


# 全局Redis客户端实例
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """获取Redis客户端依赖"""
    return redis_client

