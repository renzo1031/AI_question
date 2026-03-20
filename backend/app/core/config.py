"""
应用配置模块
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基础配置
    app_name: str = "AI智能学习系统"
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-this-in-production"
    timezone: str = "Asia/Shanghai"  # 时区配置，默认北京时间
    
    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_learning"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT配置
    jwt_secret_key: str = "jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # SM4加密密钥（必须16字节）
    sm4_secret_key: str = "1234567890abcdef"
    
    # Session配置
    session_secret_key: str = "session-secret-key-change-in-production"
    session_expire_hours: int = 24
    
    # 邮件配置
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@example.com"
    
    # 阿里云短信配置
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_sms_sign_name: str = ""
    aliyun_sms_template_code: str = ""
    
    # 阿里云OCR配置
    aliyun_ocr_endpoint: str = "https://ocr-api.cn-hangzhou.aliyuncs.com"
    
    # AI服务配置
    default_ai_provider: Literal["tongyi", "deepseek", "kimi", "openai", "custom"] = "tongyi"
    
    # 通义千问配置
    tongyi_api_key: str = ""
    tongyi_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    tongyi_model: str = "qwen-turbo"
    
    # DeepSeek配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"  # 也可以使用 https://api.deepseek.com/v1
    deepseek_model: str = "deepseek-chat"  # 可选：deepseek-chat, deepseek-reasoner
    
    # Kimi配置
    kimi_api_key: str = ""
    kimi_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
    
    # OpenAI配置（支持OpenAI官方及兼容服务）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"  # 可选：gpt-3.5-turbo, gpt-4, gpt-4-turbo等
    
    # 自定义OpenAI兼容提供商配置（用于本地模型或其他兼容服务）
    custom_ai_api_key: str = ""
    custom_ai_base_url: str = ""
    custom_ai_model: str = ""
    custom_ai_timeout: float = 60.0
    custom_ai_temperature: float = 0.3
    custom_ai_max_tokens: int = 2000

    # MinIO 对象存储配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "banners"
    minio_secure: bool = False
    minio_public_url: str = "http://localhost:9000"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()

