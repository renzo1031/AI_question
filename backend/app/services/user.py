"""
用户服务
提供用户注册、登录、信息管理等业务逻辑
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, AuthException, ErrorCode
from app.common.utils import mask_email, mask_phone
from app.core.config import settings
from app.core.redis import redis_client
from app.core.security.jwt import jwt_handler
from app.core.security.password import password_handler
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository
from app.schemas.user import LoginResponse, UserInfoResponse
from app.services.verify_code import verify_code_service


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    # ==================== 注册 ====================
    
    async def register_by_phone(
        self,
        phone: str,
        password: str,
        verify_code: str,
        nickname: Optional[str] = None
    ) -> User:
        """手机号注册"""
        # 验证验证码
        await verify_code_service.verify_code(phone, verify_code, "register")
        
        # 检查手机号是否已存在
        if await self.user_repo.exists_by_phone(phone):
            raise AppException(
                code=ErrorCode.PHONE_ALREADY_EXISTS,
                message="该手机号已被注册"
            )
        
        # 创建用户
        password_hash = password_handler.hash(password)
        user = await self.user_repo.create(
            phone=phone,
            password_hash=password_hash,
            nickname=nickname
        )
        
        return user
    
    async def register_by_email(
        self,
        email: str,
        password: str,
        verify_code: str,
        nickname: Optional[str] = None
    ) -> User:
        """邮箱注册"""
        # 验证验证码
        await verify_code_service.verify_code(email, verify_code, "register")
        
        # 检查邮箱是否已存在
        if await self.user_repo.exists_by_email(email):
            raise AppException(
                code=ErrorCode.EMAIL_ALREADY_EXISTS,
                message="该邮箱已被注册"
            )
        
        # 创建用户
        password_hash = password_handler.hash(password)
        user = await self.user_repo.create(
            email=email,
            password_hash=password_hash,
            nickname=nickname
        )
        
        return user
    
    # ==================== 登录 ====================
    
    async def login_by_password(
        self,
        account: str,
        password: str
    ) -> LoginResponse:
        """密码登录"""
        # 查找用户
        user = await self.user_repo.get_by_phone_or_email(account)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        # 检查用户状态
        self._check_user_status(user)
        
        # 验证密码
        if not password_handler.verify(password, user.password_hash):
            raise AppException(
                code=ErrorCode.PASSWORD_INCORRECT,
                message="密码错误"
            )
        
        # 更新登录时间
        await self.user_repo.update_last_login(user.id)
        
        # 生成Token
        return self._create_login_response(user)
    
    async def login_by_verify_code(
        self,
        target: str,
        verify_code: str
    ) -> LoginResponse:
        """验证码登录"""
        # 验证验证码
        await verify_code_service.verify_code(target, verify_code, "login")
        
        # 查找用户
        user = await self.user_repo.get_by_phone_or_email(target)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在，请先注册"
            )
        
        # 检查用户状态
        self._check_user_status(user)
        
        # 更新登录时间
        await self.user_repo.update_last_login(user.id)
        
        # 生成Token
        return self._create_login_response(user)
    
    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """刷新Token"""
        # 验证RefreshToken
        payload = jwt_handler.verify_refresh_token(refresh_token)
        if not payload:
            raise AuthException(
                code=ErrorCode.TOKEN_INVALID,
                message="RefreshToken无效或已过期"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException(
                code=ErrorCode.TOKEN_INVALID,
                message="Token数据无效"
            )
        
        # 检查Token是否在黑名单
        if await redis_client.is_token_blacklisted(refresh_token):
            raise AuthException(
                code=ErrorCode.TOKEN_INVALID,
                message="Token已失效"
            )
        
        # 获取用户
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        # 检查用户状态
        self._check_user_status(user)
        
        # 将旧的RefreshToken加入黑名单
        await redis_client.add_token_blacklist(
            refresh_token,
            settings.jwt_refresh_token_expire_days * 86400
        )
        
        # 生成新Token
        return self._create_login_response(user)
    
    async def logout(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """退出登录"""
        # 将AccessToken加入黑名单
        await redis_client.add_token_blacklist(
            access_token,
            settings.jwt_access_token_expire_minutes * 60
        )
        
        # 将RefreshToken加入黑名单
        if refresh_token:
            await redis_client.add_token_blacklist(
                refresh_token,
                settings.jwt_refresh_token_expire_days * 86400
            )
        
        return True
    
    # ==================== 用户信息 ====================
    
    async def get_user_info(self, user_id: int) -> UserInfoResponse:
        """获取用户信息"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        return self._user_to_response(user)
    
    async def update_user_info(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        gender: Optional[str] = None,
        birthday: Optional[datetime] = None
    ) -> UserInfoResponse:
        """更新用户信息"""
        update_data = {}
        if nickname is not None:
            update_data["nickname"] = nickname
        if avatar is not None:
            update_data["avatar"] = avatar
        if gender is not None:
            update_data["gender"] = gender
        if birthday is not None:
            update_data["birthday"] = birthday
        
        if not update_data:
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message="没有要更新的内容"
            )
        
        user = await self.user_repo.update(user_id, **update_data)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        return self._user_to_response(user)
    
    # ==================== 密码管理 ====================
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """修改密码"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        # 验证旧密码
        if not password_handler.verify(old_password, user.password_hash):
            raise AppException(
                code=ErrorCode.PASSWORD_INCORRECT,
                message="原密码错误"
            )
        
        # 更新密码
        new_hash = password_handler.hash(new_password)
        return await self.user_repo.update_password(user_id, new_hash)
    
    async def reset_password(
        self,
        target: str,
        verify_code: str,
        new_password: str
    ) -> bool:
        """重置密码"""
        # 验证验证码
        await verify_code_service.verify_code(target, verify_code, "reset_password")
        
        # 查找用户
        user = await self.user_repo.get_by_phone_or_email(target)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        # 更新密码
        new_hash = password_handler.hash(new_password)
        return await self.user_repo.update_password(user.id, new_hash)
    
    # ==================== 绑定手机/邮箱 ====================
    
    async def bind_phone(
        self,
        user_id: int,
        phone: str,
        verify_code: str
    ) -> bool:
        """绑定手机号"""
        # 验证验证码
        await verify_code_service.verify_code(phone, verify_code, "bind")
        
        # 检查手机号是否已被其他用户使用
        existing_user = await self.user_repo.get_by_phone(phone)
        if existing_user and existing_user.id != user_id:
            raise AppException(
                code=ErrorCode.PHONE_ALREADY_EXISTS,
                message="该手机号已被其他账号绑定"
            )
        
        return await self.user_repo.update_phone(user_id, phone)
    
    async def bind_email(
        self,
        user_id: int,
        email: str,
        verify_code: str
    ) -> bool:
        """绑定邮箱"""
        # 验证验证码
        await verify_code_service.verify_code(email, verify_code, "bind")
        
        # 检查邮箱是否已被其他用户使用
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user and existing_user.id != user_id:
            raise AppException(
                code=ErrorCode.EMAIL_ALREADY_EXISTS,
                message="该邮箱已被其他账号绑定"
            )
        
        return await self.user_repo.update_email(user_id, email)
    
    # ==================== 辅助方法 ====================
    
    def _check_user_status(self, user: User) -> None:
        """检查用户状态"""
        if user.status == UserStatus.DISABLED:
            raise AppException(
                code=ErrorCode.USER_DISABLED,
                message="账号已被禁用"
            )
        if user.status == UserStatus.DELETED:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
    
    def _create_login_response(self, user: User) -> LoginResponse:
        """创建登录响应"""
        # 生成Token
        token_data = {"sub": str(user.id)}
        access_token = jwt_handler.create_access_token(token_data)
        refresh_token = jwt_handler.create_refresh_token(token_data)
        
        # 计算AccessToken过期时间戳（毫秒）
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        access_expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_expire_at_ms = int(access_expires_at.timestamp() * 1000)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            access_expire_at=access_expire_at_ms,
        )
    
    def _user_to_response(self, user: User) -> UserInfoResponse:
        """将User模型转换为响应"""
        return UserInfoResponse(
            id=str(user.id),
            phone=mask_phone(user.phone) if user.phone else None,
            email=mask_email(user.email) if user.email else None,
            nickname=user.nickname,
            avatar=user.avatar,
            gender=user.gender,
            birthday=user.birthday,
            status=user.status,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )

