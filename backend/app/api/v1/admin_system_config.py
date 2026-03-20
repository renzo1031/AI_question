"""管理端系统配置API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.middleware.auth import get_current_admin_id
from app.schemas.system_config import (
    EmailConfigRequest,
    EmailConfigResponse,
    SmsConfigRequest,
    SmsConfigResponse,
    TestEmailRequest,
    TestSmsRequest,
)
from app.services.system_config_service import SystemConfigService

router = APIRouter(prefix="/admin/system-config", tags=["管理端-系统配置"])


# ==================== 邮件配置 ====================

@router.get("/email", summary="获取邮件配置")
async def get_email_config(
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """获取邮件配置"""
    service = SystemConfigService(db)
    config = await service.get_email_config()
    
    if not config:
        # 返回默认配置
        config = EmailConfigResponse(
            smtp_host="",
            smtp_port=587,
            smtp_user="",
            smtp_password="",
            smtp_from="",
            smtp_use_tls=True,
            is_enabled=False,
        )
    
    return success(data=config)


@router.post("/email", summary="更新邮件配置")
async def update_email_config(
    config: EmailConfigRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """更新邮件配置"""
    service = SystemConfigService(db)
    result = await service.update_email_config(config, admin_id)
    return success(data=result, message="邮件配置更新成功")


@router.post("/email/test", summary="测试邮件配置")
async def test_email_config(
    test_request: TestEmailRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """测试邮件配置"""
    service = SystemConfigService(db)
    await service.test_email_config(
        test_request.to_email,
        test_request.subject,
        test_request.content,
    )
    return success(message="测试邮件发送成功")


# ==================== 短信配置 ====================

@router.get("/sms", summary="获取短信配置")
async def get_sms_config(
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """获取短信配置"""
    service = SystemConfigService(db)
    config = await service.get_sms_config()
    
    if not config:
        # 返回默认配置
        config = SmsConfigResponse(
            provider="aliyun",
            is_enabled=False,
        )
    
    return success(data=config)


@router.post("/sms", summary="更新短信配置")
async def update_sms_config(
    config: SmsConfigRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """更新短信配置"""
    service = SystemConfigService(db)
    result = await service.update_sms_config(config, admin_id)
    return success(data=result, message="短信配置更新成功")


@router.post("/sms/test", summary="测试短信配置")
async def test_sms_config(
    test_request: TestSmsRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(get_current_admin_id),
):
    """测试短信配置"""
    service = SystemConfigService(db)
    await service.test_sms_config(test_request.phone, test_request.code)
    return success(message="测试短信发送成功")
