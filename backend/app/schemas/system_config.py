"""系统配置 Schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    config_key: str = Field(..., description="配置键")
    config_group: str = Field(..., description="配置分组")
    config_name: str = Field(..., description="配置名称")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置说明")
    is_encrypted: bool = Field(False, description="是否加密存储")
    is_enabled: bool = Field(True, description="是否启用")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置"""


class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    config_value: Optional[str] = Field(None, description="配置值")
    config_name: Optional[str] = Field(None, description="配置名称")
    description: Optional[str] = Field(None, description="配置说明")
    is_encrypted: Optional[bool] = Field(None, description="是否加密存储")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class SystemConfigResponse(SystemConfigBase):
    """系统配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 邮件配置
class EmailConfigRequest(BaseModel):
    """邮件配置请求"""
    smtp_host: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(..., description="SMTP端口", ge=1, le=65535)
    smtp_user: str = Field(..., description="SMTP用户名")
    smtp_password: str = Field(..., description="SMTP密码")
    smtp_from: str = Field(..., description="发件人邮箱")
    smtp_use_tls: bool = Field(True, description="是否使用TLS")
    is_enabled: bool = Field(True, description="是否启用邮件服务")


class EmailConfigResponse(BaseModel):
    """邮件配置响应"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str  # 返回时会脱敏
    smtp_from: str
    smtp_use_tls: bool
    is_enabled: bool
    updated_at: Optional[datetime] = None


# 短信配置
class SmsConfigRequest(BaseModel):
    """短信配置请求"""
    provider: str = Field("aliyun", description="短信提供商：aliyun 或 tencent")
    
    # 阿里云配置
    aliyun_access_key_id: Optional[str] = Field(None, description="阿里云AccessKey ID")
    aliyun_access_key_secret: Optional[str] = Field(None, description="阿里云AccessKey Secret")
    aliyun_sms_sign_name: Optional[str] = Field(None, description="阿里云短信签名")
    aliyun_sms_template_code: Optional[str] = Field(None, description="阿里云短信模板CODE")
    aliyun_sms_region: str = Field("cn-hangzhou", description="阿里云地域")
    
    # 腾讯云配置
    tencent_secret_id: Optional[str] = Field(None, description="腾讯云SecretId")
    tencent_secret_key: Optional[str] = Field(None, description="腾讯云SecretKey")
    tencent_sms_app_id: Optional[str] = Field(None, description="腾讯云短信应用ID")
    tencent_sms_sign_name: Optional[str] = Field(None, description="腾讯云短信签名")
    tencent_sms_template_id: Optional[str] = Field(None, description="腾讯云短信模板ID")
    tencent_sms_region: str = Field("ap-guangzhou", description="腾讯云地域")
    
    is_enabled: bool = Field(True, description="是否启用短信服务")


class SmsConfigResponse(BaseModel):
    """短信配置响应"""
    provider: str  # aliyun 或 tencent
    
    # 阿里云配置
    aliyun_access_key_id: Optional[str] = None  # 返回时会脱敏
    aliyun_access_key_secret: Optional[str] = None  # 返回时会脱敏
    aliyun_sms_sign_name: Optional[str] = None
    aliyun_sms_template_code: Optional[str] = None
    aliyun_sms_region: Optional[str] = None
    
    # 腾讯云配置
    tencent_secret_id: Optional[str] = None  # 返回时会脱敏
    tencent_secret_key: Optional[str] = None  # 返回时会脱敏
    tencent_sms_app_id: Optional[str] = None
    tencent_sms_sign_name: Optional[str] = None
    tencent_sms_template_id: Optional[str] = None
    tencent_sms_region: Optional[str] = None
    
    is_enabled: bool
    updated_at: Optional[datetime] = None


# 测试配置
class TestEmailRequest(BaseModel):
    """测试邮件请求"""
    to_email: str = Field(..., description="收件人邮箱")
    subject: str = Field("测试邮件", description="邮件主题")
    content: str = Field("这是一封测试邮件", description="邮件内容")


class TestSmsRequest(BaseModel):
    """测试短信请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field("123456", description="验证码")
