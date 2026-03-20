"""
AI解题结果缓存模块
使用Redis缓存AI解题结果，提高响应速度
"""
from typing import Awaitable, Callable, Optional

from app.core.config import settings
from app.core.redis import redis_client


class AICache:
    """AI解题结果缓存类"""
    
    # 缓存键前缀
    CACHE_KEY_PREFIX = "ai:question"
    
    # 默认TTL：7天（秒）
    DEFAULT_TTL = 7 * 24 * 60 * 60
    
    @property
    def default_ttl(self) -> int:
        """
        获取默认TTL（从配置读取或使用默认值7天）
        
        Returns:
            TTL（秒）
        """
        return getattr(settings, "ai_cache_ttl_seconds", self.DEFAULT_TTL)
    
    def _get_cache_key(self, content_hash: str, provider_name: Optional[str] = None) -> str:
        """
        生成缓存键
        
        格式: ai:question:{provider_name}:{content_hash}
        如果 provider_name 为 None，使用配置的默认提供商
        
        Args:
            content_hash: 题目内容哈希值
            provider_name: AI提供商名称（可选）
            
        Returns:
            缓存键
        """
        if provider_name:
            provider = provider_name
        else:
            # 使用配置的默认提供商
            from app.core.config import settings
            provider = getattr(settings, "default_ai_provider", "tongyi")
        return f"{self.CACHE_KEY_PREFIX}:{provider}:{content_hash}"
    
    def _validate_cache_data(self, data: dict) -> bool:
        """
        验证缓存数据格式
        
        Args:
            data: 缓存数据字典
            
        Returns:
            是否有效
        """
        required_fields = ["answer", "analysis", "question_type", "subject", "difficulty", "options"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                return False
        
        # 检查字段类型
        if not isinstance(data.get("answer"), str):
            return False
        if not isinstance(data.get("analysis"), str):
            return False
        if not isinstance(data.get("question_type"), str):
            return False
        if not isinstance(data.get("subject"), str):
            return False
        if not isinstance(data.get("difficulty"), int):
            return False
        if not isinstance(data.get("options"), list):
            return False
        
        # 检查 difficulty 范围
        difficulty = data.get("difficulty")
        if difficulty < 1 or difficulty > 5:
            return False
        
        return True
    
    async def get(
        self,
        content_hash: str,
        provider_name: Optional[str] = None
    ) -> Optional[dict]:
        """
        从缓存获取AI解题结果
        
        Args:
            content_hash: 题目内容哈希值
            provider_name: AI提供商名称（可选）
            
        Returns:
            AI解题结果字典，格式：
            {
                "answer": str,
                "analysis": str,
                "question_type": str,
                "subject": str,
                "difficulty": int,
                "options": list
            }
            如果不存在或数据格式无效则返回None
        """
        try:
            cache_key = self._get_cache_key(content_hash, provider_name)
            result = await redis_client.get_json(cache_key)
            
            # 验证缓存数据格式
            if result and self._validate_cache_data(result):
                return result
            elif result:
                # 数据格式无效，删除损坏的缓存
                from loguru import logger
                logger.warning(f"缓存数据格式无效，删除损坏的缓存: {content_hash[:16]}...")
                await self.delete(content_hash, provider_name)
                return None
            
            return None
        except Exception as e:
            from loguru import logger
            logger.warning(f"读取Redis缓存失败: {str(e)}, content_hash: {content_hash[:16]}...")
            return None
    
    async def set(
        self,
        content_hash: str,
        ai_result: dict,
        ttl: Optional[int] = None,
        provider_name: Optional[str] = None
    ) -> bool:
        """
        将AI解题结果存入缓存
        
        Args:
            content_hash: 题目内容哈希值
            ai_result: AI解题结果字典，必须包含以下字段：
                - answer: str, 答案
                - analysis: str, 解析
                - question_type: str, 题目类型
                - subject: str, 科目
                - difficulty: int, 难度（1-5）
                - options: list, 选项列表
            ttl: 过期时间（秒），如果为None则使用默认TTL（7天）
            provider_name: AI提供商名称（可选）
            
        Returns:
            是否设置成功
        """
        from loguru import logger
        from redis.asyncio import ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError
        
        # 验证数据格式
        if not self._validate_cache_data(ai_result):
            logger.error(f"AI解题结果数据格式无效，无法写入缓存: {content_hash[:16]}...")
            return False
        
        cache_key = self._get_cache_key(content_hash, provider_name)
        expire = ttl if ttl is not None else self.default_ttl
        
        try:
            # 确保Redis连接已建立
            if redis_client._client is None:
                await redis_client.connect()
            
            # 使用JSON序列化存储
            result = await redis_client.set_json(cache_key, ai_result, expire)
            return result
        except (RedisConnectionError, RedisTimeoutError) as e:
            # Redis 连接失败，记录错误但不影响主流程
            logger.warning(f"Redis连接失败，无法写入缓存: {str(e)}, content_hash: {content_hash[:16]}...")
            return False
        except Exception as e:
            # 其他错误
            logger.error(f"写入Redis缓存失败: {str(e)}, content_hash: {content_hash[:16]}...", exc_info=True)
            return False
    
    async def delete(
        self,
        content_hash: str,
        provider_name: Optional[str] = None
    ) -> int:
        """
        删除缓存
        
        Args:
            content_hash: 题目内容哈希值
            provider_name: AI提供商名称（可选）
            
        Returns:
            删除的键数量
        """
        cache_key = self._get_cache_key(content_hash, provider_name)
        return await redis_client.delete(cache_key)
    
    async def exists(
        self,
        content_hash: str,
        provider_name: Optional[str] = None
    ) -> bool:
        """
        检查缓存是否存在
        
        Args:
            content_hash: 题目内容哈希值
            provider_name: AI提供商名称（可选）
            
        Returns:
            是否存在
        """
        cache_key = self._get_cache_key(content_hash, provider_name)
        return await redis_client.exists(cache_key)
    
    async def get_or_set(
        self,
        content_hash: str,
        fetch_func: Callable[[], Awaitable[dict]],
        ttl: Optional[int] = None
    ) -> dict:
        """
        获取缓存，如果不存在则调用函数获取并缓存
        
        Args:
            content_hash: 题目内容哈希值
            fetch_func: 异步函数，用于获取AI解题结果
            ttl: 过期时间（秒），如果为None则使用默认TTL
            
        Returns:
            AI解题结果字典
        """
        # 先尝试从缓存获取
        cached_result = await self.get(content_hash)
        if cached_result is not None:
            return cached_result
        
        # 缓存未命中，调用函数获取结果
        ai_result = await fetch_func()
        
        # 存入缓存
        await self.set(content_hash, ai_result, ttl)
        
        return ai_result
    
    async def get_ttl(
        self,
        content_hash: str,
        provider_name: Optional[str] = None
    ) -> int:
        """
        获取缓存的剩余过期时间
        
        Args:
            content_hash: 题目内容哈希值
            provider_name: AI提供商名称（可选）
            
        Returns:
            剩余过期时间（秒），-1表示永不过期，-2表示不存在
        """
        cache_key = self._get_cache_key(content_hash, provider_name)
        return await redis_client.ttl(cache_key)


# 全局AI缓存实例
ai_cache = AICache()

