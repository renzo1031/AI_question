"""
AI模型管理器
负责管理和调度不同的AI模型提供商
"""
from typing import Optional

from app.core.config import settings
from app.core.ai.base import AIModelProvider
from app.core.ai.tongyi import TongYiProvider
from app.core.ai.deepseek import DeepSeekProvider
from app.core.ai.kimi import KimiProvider
from app.core.ai.openai_compatible import OpenAICompatibleProvider


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.providers: dict[str, AIModelProvider] = {}
        self._init_providers()
    
    def _init_providers(self):
        """初始化所有可用的AI提供商"""
        # 通义千问
        if settings.tongyi_api_key:
            self.providers["tongyi"] = TongYiProvider(
                api_key=settings.tongyi_api_key,
                model=getattr(settings, "tongyi_model", "qwen-turbo"),
                base_url=getattr(settings, "tongyi_base_url", None)
            )
        
        # DeepSeek
        if settings.deepseek_api_key:
            self.providers["deepseek"] = DeepSeekProvider(
                api_key=settings.deepseek_api_key,
                base_url=getattr(settings, "deepseek_base_url", "https://api.deepseek.com"),
                model=getattr(settings, "deepseek_model", "deepseek-chat")
            )
        
        # Kimi
        if settings.kimi_api_key:
            self.providers["kimi"] = KimiProvider(
                api_key=settings.kimi_api_key,
                base_url=getattr(settings, "kimi_base_url", "https://api.moonshot.cn/v1"),
                model=getattr(settings, "kimi_model", "moonshot-v1-8k")
            )
        
        # OpenAI（官方及兼容服务）
        if settings.openai_api_key:
            self.providers["openai"] = OpenAICompatibleProvider(
                api_key=settings.openai_api_key,
                base_url=getattr(settings, "openai_base_url", "https://api.openai.com/v1"),
                model=getattr(settings, "openai_model", "gpt-3.5-turbo"),
                provider_name="openai"
            )
        
        # 自定义OpenAI兼容提供商（用于本地模型或其他兼容服务）
        if settings.custom_ai_api_key and settings.custom_ai_base_url and settings.custom_ai_model:
            self.providers["custom"] = OpenAICompatibleProvider(
                api_key=settings.custom_ai_api_key,
                base_url=settings.custom_ai_base_url,
                model=settings.custom_ai_model,
                provider_name="custom",
                timeout=getattr(settings, "custom_ai_timeout", 60.0),
                temperature=getattr(settings, "custom_ai_temperature", 0.3),
                max_tokens=getattr(settings, "custom_ai_max_tokens", 2000)
            )
    
    def get_provider(self, provider_name: Optional[str] = None) -> AIModelProvider:
        """
        获取AI提供商
        
        Args:
            provider_name: 提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
            
        Returns:
            AI模型提供商实例
            
        Raises:
            ValueError: 当指定的提供商不可用时
        """
        if not provider_name:
            provider_name = getattr(settings, "default_ai_provider", "tongyi")
        
        provider = self.providers.get(provider_name)
        if not provider:
            available = ", ".join(self.providers.keys())
            raise ValueError(
                f"AI提供商 '{provider_name}' 不可用。"
                f"可用提供商: {available if available else '无'}"
            )
        
        return provider
    
    async def solve_question(
        self,
        question: str,
        provider_name: Optional[str] = None,
        context: Optional[str] = None
    ) -> dict:
        """
        解题
        
        Args:
            question: 题目内容
            provider_name: 提供商名称（可选）
            context: 上下文信息（可选）
            
        Returns:
            包含答案和解析的字典
        """
        provider = self.get_provider(provider_name)
        return await provider.solve_question(question, context)
    
    def list_available_providers(self) -> list[str]:
        """列出所有可用的提供商"""
        return list(self.providers.keys())


# 全局AI模型管理器实例
ai_model_manager = AIModelManager()

