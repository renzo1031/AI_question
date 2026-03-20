"""系统配置服务"""
from typing import Optional

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode
from app.core.security.sm4 import sm4_encrypt, sm4_decrypt
from app.repositories.system_config_repo import SystemConfigRepository
from app.schemas.system_config import (
    EmailConfigRequest,
    EmailConfigResponse,
    SmsConfigRequest,
    SmsConfigResponse,
)


class SystemConfigService:
    """系统配置服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_repo = SystemConfigRepository(db)

    # ==================== 邮件配置 ====================

    async def get_email_config(self) -> Optional[EmailConfigResponse]:
        """获取邮件配置"""
        configs = await self.config_repo.get_by_group("email")
        
        if not configs:
            return None

        config_dict = {cfg.config_key: cfg for cfg in configs}
        
        # 解密密码
        smtp_password = ""
        if "email.smtp_password" in config_dict:
            password_config = config_dict["email.smtp_password"]
            if password_config.is_encrypted:
                try:
                    smtp_password = sm4_decrypt(password_config.config_value)
                except Exception as e:
                    logger.error(f"Failed to decrypt SMTP password: {e}")
                    smtp_password = "******"
            else:
                smtp_password = password_config.config_value
        
        # 脱敏密码
        smtp_password = self._mask_sensitive(smtp_password)
        
        return EmailConfigResponse(
            smtp_host=config_dict.get("email.smtp_host", {}).config_value if "email.smtp_host" in config_dict else "",
            smtp_port=int(config_dict.get("email.smtp_port", {}).config_value) if "email.smtp_port" in config_dict else 587,
            smtp_user=config_dict.get("email.smtp_user", {}).config_value if "email.smtp_user" in config_dict else "",
            smtp_password=smtp_password,
            smtp_from=config_dict.get("email.smtp_from", {}).config_value if "email.smtp_from" in config_dict else "",
            smtp_use_tls=config_dict.get("email.smtp_use_tls", {}).config_value == "true" if "email.smtp_use_tls" in config_dict else True,
            is_enabled=config_dict.get("email.enabled", {}).config_value == "true" if "email.enabled" in config_dict else False,
            updated_at=config_dict.get("email.smtp_host", {}).updated_at if "email.smtp_host" in config_dict else None,
        )

    async def update_email_config(
        self, 
        config: EmailConfigRequest, 
        admin_id: str
    ) -> EmailConfigResponse:
        """更新邮件配置"""
        # 加密密码
        encrypted_password = sm4_encrypt(config.smtp_password)
        
        # 批量更新配置
        configs_to_update = [
            ("email.smtp_host", "email", "SMTP服务器", config.smtp_host, False),
            ("email.smtp_port", "email", "SMTP端口", str(config.smtp_port), False),
            ("email.smtp_user", "email", "SMTP用户名", config.smtp_user, False),
            ("email.smtp_password", "email", "SMTP密码", encrypted_password, True),
            ("email.smtp_from", "email", "发件人邮箱", config.smtp_from, False),
            ("email.smtp_use_tls", "email", "使用TLS", "true" if config.smtp_use_tls else "false", False),
            ("email.enabled", "email", "启用邮件服务", "true" if config.is_enabled else "false", False),
        ]
        
        for key, group, name, value, is_encrypted in configs_to_update:
            await self.config_repo.upsert(
                config_key=key,
                config_group=group,
                config_name=name,
                config_value=value,
                is_encrypted=is_encrypted,
                is_enabled=True,
                admin_id=admin_id,
            )
        
        await self.db.commit()
        
        # 返回更新后的配置
        return await self.get_email_config()

    async def test_email_config(self, to_email: str, subject: str, content: str) -> bool:
        """测试邮件配置"""
        config = await self.get_email_config()
        
        if not config or not config.is_enabled:
            raise AppException(
                code=ErrorCode.CONFIG_ERROR,
                message="邮件服务未配置或未启用"
            )
        
        # 获取未脱敏的密码
        password_config = await self.config_repo.get_by_key("email.smtp_password")
        if not password_config:
            raise AppException(
                code=ErrorCode.CONFIG_ERROR,
                message="SMTP密码未配置"
            )
        
        smtp_password = sm4_decrypt(password_config.config_value) if password_config.is_encrypted else password_config.config_value
        
        try:
            # 创建邮件
            message = MIMEMultipart()
            message["From"] = config.smtp_from
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MIMEText(content, "plain", "utf-8"))
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=config.smtp_host,
                port=config.smtp_port,
                username=config.smtp_user,
                password=smtp_password,
                use_tls=config.smtp_use_tls,
            )
            
            logger.info(f"Test email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"邮件发送失败: {str(e)}"
            )

    # ==================== 短信配置 ====================

    async def get_sms_config(self) -> Optional[SmsConfigResponse]:
        """获取短信配置"""
        configs = await self.config_repo.get_by_group("sms")
        
        if not configs:
            return None

        config_dict = {cfg.config_key: cfg for cfg in configs}
        
        # 获取提供商
        provider = config_dict.get("sms.provider", {}).config_value if "sms.provider" in config_dict else "aliyun"
        
        # 准备响应数据
        response_data = {
            "provider": provider,
            "is_enabled": config_dict.get("sms.enabled", {}).config_value == "true" if "sms.enabled" in config_dict else False,
            "updated_at": None,
        }
        
        # 阿里云配置
        if "sms.aliyun_access_key_id" in config_dict:
            key_id_config = config_dict["sms.aliyun_access_key_id"]
            access_key_id = self._decrypt_and_mask(key_id_config)
            response_data["aliyun_access_key_id"] = access_key_id
            response_data["updated_at"] = key_id_config.updated_at
        
        if "sms.aliyun_access_key_secret" in config_dict:
            key_secret_config = config_dict["sms.aliyun_access_key_secret"]
            response_data["aliyun_access_key_secret"] = self._decrypt_and_mask(key_secret_config)
        
        response_data["aliyun_sms_sign_name"] = config_dict.get("sms.aliyun_sms_sign_name", {}).config_value if "sms.aliyun_sms_sign_name" in config_dict else None
        response_data["aliyun_sms_template_code"] = config_dict.get("sms.aliyun_sms_template_code", {}).config_value if "sms.aliyun_sms_template_code" in config_dict else None
        response_data["aliyun_sms_region"] = config_dict.get("sms.aliyun_sms_region", {}).config_value if "sms.aliyun_sms_region" in config_dict else None
        
        # 腾讯云配置
        if "sms.tencent_secret_id" in config_dict:
            secret_id_config = config_dict["sms.tencent_secret_id"]
            response_data["tencent_secret_id"] = self._decrypt_and_mask(secret_id_config)
            if not response_data["updated_at"]:
                response_data["updated_at"] = secret_id_config.updated_at
        
        if "sms.tencent_secret_key" in config_dict:
            secret_key_config = config_dict["sms.tencent_secret_key"]
            response_data["tencent_secret_key"] = self._decrypt_and_mask(secret_key_config)
        
        response_data["tencent_sms_app_id"] = config_dict.get("sms.tencent_sms_app_id", {}).config_value if "sms.tencent_sms_app_id" in config_dict else None
        response_data["tencent_sms_sign_name"] = config_dict.get("sms.tencent_sms_sign_name", {}).config_value if "sms.tencent_sms_sign_name" in config_dict else None
        response_data["tencent_sms_template_id"] = config_dict.get("sms.tencent_sms_template_id", {}).config_value if "sms.tencent_sms_template_id" in config_dict else None
        response_data["tencent_sms_region"] = config_dict.get("sms.tencent_sms_region", {}).config_value if "sms.tencent_sms_region" in config_dict else None
        
        return SmsConfigResponse(**response_data)

    async def update_sms_config(
        self, 
        config: SmsConfigRequest, 
        admin_id: str
    ) -> SmsConfigResponse:
        """更新短信配置"""
        configs_to_update = [
            ("sms.provider", "sms", "短信提供商", config.provider, False),
            ("sms.enabled", "sms", "启用短信服务", "true" if config.is_enabled else "false", False),
        ]
        
        # 阿里云配置
        if config.provider == "aliyun":
            if not config.aliyun_access_key_id or not config.aliyun_access_key_secret:
                raise AppException(
                    code=ErrorCode.PARAM_ERROR,
                    message="阿里云配置缺少必要参数"
                )
            
            configs_to_update.extend([
                ("sms.aliyun_access_key_id", "sms", "AccessKey ID", sm4_encrypt(config.aliyun_access_key_id), True),
                ("sms.aliyun_access_key_secret", "sms", "AccessKey Secret", sm4_encrypt(config.aliyun_access_key_secret), True),
                ("sms.aliyun_sms_sign_name", "sms", "阿里云短信签名", config.aliyun_sms_sign_name or "", False),
                ("sms.aliyun_sms_template_code", "sms", "阿里云模板CODE", config.aliyun_sms_template_code or "", False),
                ("sms.aliyun_sms_region", "sms", "阿里云地域", config.aliyun_sms_region, False),
            ])
        
        # 腾讯云配置
        elif config.provider == "tencent":
            if not config.tencent_secret_id or not config.tencent_secret_key:
                raise AppException(
                    code=ErrorCode.PARAM_ERROR,
                    message="腾讯云配置缺少必要参数"
                )
            
            configs_to_update.extend([
                ("sms.tencent_secret_id", "sms", "SecretId", sm4_encrypt(config.tencent_secret_id), True),
                ("sms.tencent_secret_key", "sms", "SecretKey", sm4_encrypt(config.tencent_secret_key), True),
                ("sms.tencent_sms_app_id", "sms", "腾讯云短信应用ID", config.tencent_sms_app_id or "", False),
                ("sms.tencent_sms_sign_name", "sms", "腾讯云短信签名", config.tencent_sms_sign_name or "", False),
                ("sms.tencent_sms_template_id", "sms", "腾讯云模板ID", config.tencent_sms_template_id or "", False),
                ("sms.tencent_sms_region", "sms", "腾讯云地域", config.tencent_sms_region, False),
            ])
        
        # 批量更新
        for key, group, name, value, is_encrypted in configs_to_update:
            await self.config_repo.upsert(
                config_key=key,
                config_group=group,
                config_name=name,
                config_value=value,
                is_encrypted=is_encrypted,
                is_enabled=True,
                admin_id=admin_id,
            )
        
        await self.db.commit()
        
        # 返回更新后的配置
        return await self.get_sms_config()

    async def test_sms_config(self, phone: str, code: str) -> bool:
        """测试短信配置"""
        config = await self.get_sms_config()
        
        if not config or not config.is_enabled:
            raise AppException(
                code=ErrorCode.CONFIG_ERROR,
                message="短信服务未配置或未启用"
            )
        
        try:
            if config.provider == "aliyun":
                await self._test_aliyun_sms(phone, code, config)
            elif config.provider == "tencent":
                await self._test_tencent_sms(phone, code, config)
            else:
                raise AppException(
                    code=ErrorCode.CONFIG_ERROR,
                    message=f"不支持的短信提供商: {config.provider}"
                )
            
            return True
            
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Failed to send test SMS: {e}")
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"短信发送失败: {str(e)}"
            )
    
    async def _test_aliyun_sms(self, phone: str, code: str, config: SmsConfigResponse):
        """测试阿里云短信"""
        key_id_config = await self.config_repo.get_by_key("sms.aliyun_access_key_id")
        key_secret_config = await self.config_repo.get_by_key("sms.aliyun_access_key_secret")
        
        if not key_id_config or not key_secret_config:
            raise AppException(
                code=ErrorCode.CONFIG_ERROR,
                message="阿里云密钥未配置"
            )
        
        access_key_id = sm4_decrypt(key_id_config.config_value) if key_id_config.is_encrypted else key_id_config.config_value
        access_key_secret = sm4_decrypt(key_secret_config.config_value) if key_secret_config.is_encrypted else key_secret_config.config_value
        
        # TODO: 实际调用阿里云短信API
        # from alibabacloud_dysmsapi20170525.client import Client
        # from alibabacloud_tea_openapi import models as open_api_models
        # from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
        
        logger.info(f"[阿里云测试] SMS would be sent to {phone} with code {code}")
        logger.info(f"Using config: sign={config.aliyun_sms_sign_name}, template={config.aliyun_sms_template_code}")
    
    async def _test_tencent_sms(self, phone: str, code: str, config: SmsConfigResponse):
        """测试腾讯云短信"""
        secret_id_config = await self.config_repo.get_by_key("sms.tencent_secret_id")
        secret_key_config = await self.config_repo.get_by_key("sms.tencent_secret_key")
        
        if not secret_id_config or not secret_key_config:
            raise AppException(
                code=ErrorCode.CONFIG_ERROR,
                message="腾讯云密钥未配置"
            )
        
        secret_id = sm4_decrypt(secret_id_config.config_value) if secret_id_config.is_encrypted else secret_id_config.config_value
        secret_key = sm4_decrypt(secret_key_config.config_value) if secret_key_config.is_encrypted else secret_key_config.config_value
        
        # TODO: 实际调用腾讯云短信API
        # from tencentcloud.common import credential
        # from tencentcloud.sms.v20210111 import sms_client, models
        
        logger.info(f"[腾讯云测试] SMS would be sent to {phone} with code {code}")
        logger.info(f"Using config: app_id={config.tencent_sms_app_id}, sign={config.tencent_sms_sign_name}, template={config.tencent_sms_template_id}")

    # ==================== 辅助方法 ====================

    def _decrypt_and_mask(self, config) -> str:
        """解密并脱敏配置值"""
        if config.is_encrypted:
            try:
                decrypted = sm4_decrypt(config.config_value)
                return self._mask_sensitive(decrypted)
            except Exception as e:
                logger.error(f"Failed to decrypt config: {e}")
                return "******"
        else:
            return self._mask_sensitive(config.config_value)
    
    def _mask_sensitive(self, value: str, show_len: int = 4) -> str:
        """脱敏敏感信息"""
        if not value or len(value) <= show_len:
            return "******"
        return value[:show_len] + "******"

    async def get_config_value(self, config_key: str, decrypt: bool = False) -> Optional[str]:
        """获取配置值"""
        config = await self.config_repo.get_by_key(config_key)
        if not config:
            return None
        
        if decrypt and config.is_encrypted:
            try:
                return sm4_decrypt(config.config_value)
            except Exception as e:
                logger.error(f"Failed to decrypt config {config_key}: {e}")
                return None
        
        return config.config_value
