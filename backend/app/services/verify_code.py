"""
验证码服务
提供验证码发送和验证功能
"""

from loguru import logger

from app.common.exceptions import AppException, ErrorCode
from app.common.utils import generate_verify_code, is_valid_email, is_valid_phone
from app.core.config import settings
from app.core.redis import redis_client


class VerifyCodeService:
    """验证码服务类"""
    
    # 验证码有效期（秒）
    CODE_EXPIRE = 300  # 5分钟
    # 发送间隔限制（秒）
    SEND_INTERVAL = 60  # 1分钟
    # 每日发送次数限制
    DAILY_LIMIT = 30
    
    def __init__(self):
        pass
    
    async def send_code(self, target: str, scene: str = "register") -> bool:
        """
        发送验证码
        
        Args:
            target: 手机号或邮箱
            scene: 场景（register, login, reset_password, bind）
            
        Returns:
            是否发送成功
        """
        # 判断是手机还是邮箱
        is_phone = is_valid_phone(target)
        is_email = is_valid_email(target)
        
        if not is_phone and not is_email:
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message="请输入正确的手机号或邮箱"
            )
        
        # 检查发送频率
        await self._check_send_limit(target)
        
        # 生成验证码
        code = generate_verify_code(6)
        
        # 保存验证码到Redis
        key = f"{scene}:{target}"
        await redis_client.set_verify_code(key, code, self.CODE_EXPIRE)
        
        # 记录发送次数
        await self._record_send(target)
        
        # 发送验证码
        if is_phone:
            success = await self._send_sms(target, code, scene)
        else:
            success = await self._send_email(target, code, scene)
        
        if not success:
            # 发送失败，删除验证码
            await redis_client.delete_verify_code(key)
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message="验证码发送失败，请稍后重试"
            )
        
        logger.info(f"Verification code sent: target={target}, scene={scene}")
        return True
    
    async def verify_code(
        self, 
        target: str, 
        code: str, 
        scene: str = "register",
        delete_after_verify: bool = True
    ) -> bool:
        """
        验证验证码
        
        Args:
            target: 手机号或邮箱
            code: 验证码
            scene: 场景
            delete_after_verify: 验证成功后是否删除
            
        Returns:
            验证是否通过
        """
        key = f"{scene}:{target}"
        stored_code = await redis_client.get_verify_code(key)
        
        if not stored_code:
            raise AppException(
                code=ErrorCode.VERIFY_CODE_EXPIRED,
                message="验证码已过期，请重新获取"
            )
        
        if stored_code != code:
            raise AppException(
                code=ErrorCode.VERIFY_CODE_INCORRECT,
                message="验证码错误"
            )
        
        # 验证成功，删除验证码
        if delete_after_verify:
            await redis_client.delete_verify_code(key)
        
        return True
    
    async def _check_send_limit(self, target: str) -> None:
        """检查发送限制"""
        # 检查发送间隔
        interval_key = f"verify_interval:{target}"
        if await redis_client.exists(interval_key):
            ttl = await redis_client.ttl(interval_key)
            raise AppException(
                code=ErrorCode.TOO_MANY_REQUESTS,
                message=f"请{ttl}秒后再试"
            )
        
        # 检查每日发送次数
        daily_key = f"verify_daily:{target}"
        daily_count = await redis_client.get(daily_key)
        if daily_count and int(daily_count) >= self.DAILY_LIMIT:
            raise AppException(
                code=ErrorCode.TOO_MANY_REQUESTS,
                message="今日发送次数已达上限"
            )
    
    async def _record_send(self, target: str) -> None:
        """记录发送"""
        # 设置发送间隔
        interval_key = f"verify_interval:{target}"
        await redis_client.set(interval_key, "1", self.SEND_INTERVAL)
        
        # 增加每日发送次数
        daily_key = f"verify_daily:{target}"
        daily_count = await redis_client.get(daily_key)
        if daily_count:
            await redis_client.set(daily_key, str(int(daily_count) + 1), 86400)
        else:
            await redis_client.set(daily_key, "1", 86400)
    
    async def _send_sms(self, phone: str, code: str, scene: str) -> bool:
        """
        发送短信验证码
        
        注意：这里需要接入实际的短信服务
        当前为模拟实现，开发环境直接返回成功
        """
        if settings.is_development:
            logger.info(f"[DEV] SMS code: {phone} -> {code}")
            return True
        
        # TODO: 接入阿里云短信服务
        # try:
        #     from alibabacloud_dysmsapi20170525.client import Client
        #     ...
        # except Exception as e:
        #     logger.error(f"Send SMS failed: {e}")
        #     return False
        
        return True
    
    async def _send_email(self, email: str, code: str, scene: str) -> bool:
        """
        发送邮件验证码
        
        注意：这里需要接入实际的邮件服务
        当前为模拟实现，开发环境直接返回成功
        """
        if settings.is_development:
            logger.info(f"[DEV] Email code: {email} -> {code}")
            return True
        
        # TODO: 接入邮件服务
        # try:
        #     import aiosmtplib
        #     ...
        # except Exception as e:
        #     logger.error(f"Send email failed: {e}")
        #     return False
        
        return True


# 全局验证码服务实例
verify_code_service = VerifyCodeService()

