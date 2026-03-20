# AI核心模块：OCR识别和AI大模型服务
from app.core.ai.base import AIModelProvider
from app.core.ai.manager import AIModelManager, ai_model_manager
from app.core.ai.tongyi import TongYiProvider
from app.core.ai.deepseek import DeepSeekProvider
from app.core.ai.kimi import KimiProvider

__all__ = [
    "AIModelProvider",
    "AIModelManager",
    "ai_model_manager",
    "TongYiProvider",
    "DeepSeekProvider",
    "KimiProvider",
]
