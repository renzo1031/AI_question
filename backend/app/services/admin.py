"""
管理员服务
提供管理员注册、登录、管理员管理、用户管理等业务逻辑
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, AuthException, ErrorCode
from app.core.security.password import password_handler
from app.core.security.session import session_manager
from app.models.user import Admin, User, UserStatus
from app.repositories.user import AdminRepository, UserRepository
from app.schemas.admin import (
    AdminInfoResponse,
    UpdateAdminRequest,
    UserDetailResponse,
)
from app.services.ability_growth_service import AbilityGrowthService
from app.services.learning_stats_service import LearningStatsService
from app.services.progress_feedback_service import ProgressFeedbackService
from app.services.verify_code import verify_code_service


class AdminService:
    """管理员服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.user_repo = UserRepository(db)
    
    # ==================== 注册 ====================
    
    async def register_by_phone(
        self,
        phone: str,
        password: str,
        username: str,
        verify_code: str
    ) -> Admin:
        """手机号注册管理员"""
        # 验证验证码
        await verify_code_service.verify_code(phone, verify_code, "register")
        
        # 检查手机号是否已存在
        if await self.admin_repo.exists_by_phone(phone):
            raise AppException(
                code=ErrorCode.ADMIN_ALREADY_EXISTS,
                message="该手机号已被注册"
            )
        
        # 创建管理员
        password_hash = password_handler.hash(password)
        admin = await self.admin_repo.create(
            password_hash=password_hash,
            username=username,
            name=username,
            phone=phone
        )
        
        return admin
    
    async def register_by_email(
        self,
        email: str,
        password: str,
        username: str,
        verify_code: str
    ) -> Admin:
        """邮箱注册管理员"""
        # 验证验证码
        await verify_code_service.verify_code(email, verify_code, "register")
        
        # 检查邮箱是否已存在
        if await self.admin_repo.exists_by_email(email):
            raise AppException(
                code=ErrorCode.ADMIN_ALREADY_EXISTS,
                message="该邮箱已被注册"
            )
        
        # 创建管理员
        password_hash = password_handler.hash(password)
        admin = await self.admin_repo.create(
            password_hash=password_hash,
            username=username,
            name=username,
            email=email
        )
        
        return admin
    
    # ==================== 登录登出 ====================
    
    async def login_by_password(
        self,
        account: str,
        password: str
    ) -> str:
        """
        管理员密码登录
        
        Returns:
            session_cookie: Session Cookie
        """
        # 查找管理员
        admin = await self.admin_repo.get_by_phone_or_email(account)
        if not admin:
            raise AuthException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="账号或密码错误"
            )
        
        # 检查状态
        if not admin.is_active:
            raise AuthException(
                code=ErrorCode.ADMIN_DISABLED,
                message="账号已被禁用"
            )
        
        # 验证密码
        if not password_handler.verify(password, admin.password_hash):
            raise AuthException(
                code=ErrorCode.ADMIN_PASSWORD_INCORRECT,
                message="账号或密码错误"
            )
        
        # 更新登录时间
        await self.admin_repo.update_last_login(admin.id)
        
        # 创建Session
        session_data = {}
        session_cookie = await session_manager.create_session(str(admin.id), session_data)
        
        return session_cookie
    
    async def login_by_verify_code(
        self,
        account: str,
        verify_code: str
    ) -> str:
        """
        管理员验证码登录
        
        Returns:
            session_cookie: Session Cookie
        """
        # 验证验证码
        await verify_code_service.verify_code(account, verify_code, "login")
        
        # 查找管理员
        admin = await self.admin_repo.get_by_phone_or_email(account)
        if not admin:
            raise AuthException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在，请先注册"
            )
        
        # 检查状态
        if not admin.is_active:
            raise AuthException(
                code=ErrorCode.ADMIN_DISABLED,
                message="账号已被禁用"
            )
        
        # 更新登录时间
        await self.admin_repo.update_last_login(admin.id)
        
        # 创建Session
        session_data = {}
        session_cookie = await session_manager.create_session(str(admin.id), session_data)
        
        return session_cookie
    
    async def logout(self, session_cookie: str) -> bool:
        """管理员登出"""
        return await session_manager.destroy_session(session_cookie)
    
    # ==================== 管理员信息 ====================
    
    async def get_current_admin(self, admin_id: str) -> AdminInfoResponse:
        """获取当前管理员信息"""
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        return self._admin_to_response(admin)
    
    async def update_current_admin(
        self,
        admin_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> AdminInfoResponse:
        """更新当前管理员信息"""
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if phone is not None:
            # 检查手机号是否已被其他管理员使用
            existing = await self.admin_repo.get_by_phone(phone)
            if existing and existing.id != admin_id:
                raise AppException(
                    code=ErrorCode.ADMIN_ALREADY_EXISTS,
                    message="该手机号已被使用"
                )
            update_data["phone"] = phone
        if email is not None:
            # 检查邮箱是否已被其他管理员使用
            existing = await self.admin_repo.get_by_email(email)
            if existing and existing.id != admin_id:
                raise AppException(
                    code=ErrorCode.ADMIN_ALREADY_EXISTS,
                    message="该邮箱已被使用"
                )
            update_data["email"] = email
        
        if not update_data:
            admin = await self.admin_repo.get_by_id(admin_id)
        else:
            admin = await self.admin_repo.update(admin_id, **update_data)
        
        if not admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        return self._admin_to_response(admin)
    
    async def change_password(
        self,
        admin_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """修改密码"""
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        # 验证旧密码
        if not password_handler.verify(old_password, admin.password_hash):
            raise AppException(
                code=ErrorCode.ADMIN_PASSWORD_INCORRECT,
                message="原密码错误"
            )
        
        # 更新密码
        new_hash = password_handler.hash(new_password)
        return await self.admin_repo.update_password(admin_id, new_hash)
    
    # ==================== 管理员管理 ====================
    
    async def create_admin(
        self,
        operator_id: int,
        password: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> AdminInfoResponse:
        """创建管理员"""
        # 检查手机号或邮箱至少有一个
        if not phone and not email:
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message="手机号和邮箱至少填写一个"
            )
        
        # 检查手机号是否已存在
        if phone and await self.admin_repo.exists_by_phone(phone):
            raise AppException(
                code=ErrorCode.ADMIN_ALREADY_EXISTS,
                message="该手机号已被注册"
            )
        
        # 检查邮箱是否已存在
        if email and await self.admin_repo.exists_by_email(email):
            raise AppException(
                code=ErrorCode.ADMIN_ALREADY_EXISTS,
                message="该邮箱已被注册"
            )
        
        # 创建管理员
        password_hash = password_handler.hash(password)
        admin = await self.admin_repo.create(
            password_hash=password_hash,
            name=name,
            phone=phone,
            email=email
        )
        
        return self._admin_to_response(admin)
    
    async def get_admin(self, admin_id: int) -> AdminInfoResponse:
        """获取管理员详情"""
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        return self._admin_to_response(admin)
    
    async def update_admin(
        self,
        operator_id: int,
        admin_id: int,
        data: UpdateAdminRequest
    ) -> AdminInfoResponse:
        """更新管理员"""
        # 获取目标管理员
        target_admin = await self.admin_repo.get_by_id(admin_id)
        if not target_admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        # 不能禁用自己
        if admin_id == operator_id and data.is_active is False:
            raise AppException(
                code=ErrorCode.PERMISSION_DENIED,
                message="不能禁用自己"
            )
        
        # 构建更新数据
        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.phone is not None:
            # 检查手机号是否已被其他管理员使用
            existing = await self.admin_repo.get_by_phone(data.phone)
            if existing and existing.id != admin_id:
                raise AppException(
                    code=ErrorCode.ADMIN_ALREADY_EXISTS,
                    message="该手机号已被使用"
                )
            update_data["phone"] = data.phone
        if data.email is not None:
            # 检查邮箱是否已被其他管理员使用
            existing = await self.admin_repo.get_by_email(data.email)
            if existing and existing.id != admin_id:
                raise AppException(
                    code=ErrorCode.ADMIN_ALREADY_EXISTS,
                    message="该邮箱已被使用"
                )
            update_data["email"] = data.email
        if data.is_active is not None:
            update_data["is_active"] = data.is_active
        
        if update_data:
            admin = await self.admin_repo.update(admin_id, **update_data)
        else:
            admin = target_admin
        
        return self._admin_to_response(admin)
    
    async def reset_admin_password(
        self,
        admin_id: int,
        new_password: str
    ) -> bool:
        """重置管理员密码"""
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        # 更新密码
        new_hash = password_handler.hash(new_password)
        return await self.admin_repo.update_password(admin_id, new_hash)
    
    async def delete_admin(self, operator_id: int, admin_id: int) -> bool:
        """删除管理员"""
        # 不能删除自己
        if admin_id == operator_id:
            raise AppException(
                code=ErrorCode.PERMISSION_DENIED,
                message="不能删除自己"
            )
        
        # 获取目标管理员
        target_admin = await self.admin_repo.get_by_id(admin_id)
        if not target_admin:
            raise AppException(
                code=ErrorCode.ADMIN_NOT_FOUND,
                message="管理员不存在"
            )
        
        return await self.admin_repo.delete(admin_id)
    
    async def get_admin_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[list[AdminInfoResponse], int]:
        """获取管理员列表"""
        admins, total = await self.admin_repo.get_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            is_active=is_active
        )
        
        return [self._admin_to_response(admin) for admin in admins], total
    
    # ==================== 用户管理（管理员使用） ====================
    
    async def get_user_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        last_login_from: Optional[datetime] = None,
        last_login_to: Optional[datetime] = None
    ) -> tuple[list[UserDetailResponse], int]:
        """获取用户列表"""
        user_status = None
        if status:
            user_status = UserStatus(status)
        
        users, total = await self.user_repo.get_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=user_status,
            created_from=created_from,
            created_to=created_to,
            last_login_from=last_login_from,
            last_login_to=last_login_to
        )
        
        return [self._user_to_detail_response(user) for user in users], total
    
    async def get_user_detail(self, user_id: str) -> UserDetailResponse:
        """获取用户详情"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        
        return self._user_to_detail_response(user)
    
    async def update_user_status(self, user_id: str, status: str) -> UserDetailResponse:
        """更新用户状态"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )

        user_status = UserStatus(status)
        await self.user_repo.update_status(user_id, user_status)
        
        # 重新获取用户
        user = await self.user_repo.get_by_id(user_id)
        return self._user_to_detail_response(user)

    async def update_user_status_with_reason(
        self,
        user_id: str,
        status: str,
        disabled_reason: Optional[str] = None
    ) -> UserDetailResponse:
        """更新用户状态（支持禁用原因）"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )

        user_status = UserStatus(status)
        if user_status == UserStatus.DISABLED:
            await self.user_repo.disable_user(user_id, reason=disabled_reason)
        else:
            await self.user_repo.update_status(user_id, user_status)

        user = await self.user_repo.get_by_id(user_id)
        return self._user_to_detail_response(user)

    async def reset_user_password(self, user_id: str, new_password: str) -> bool:
        """管理员重置用户密码"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )
        new_hash = password_handler.hash(new_password)
        return await self.user_repo.update_password(user_id, new_hash)

    async def get_user_learning_data(
        self,
        user_id: str,
        time_window_days: int = 30
    ) -> dict:
        """获取用户学习数据（管理端查看）"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.USER_NOT_FOUND,
                message="用户不存在"
            )

        overview_service = LearningStatsService(self.db)
        ability_service = AbilityGrowthService(self.db)
        feedback_service = ProgressFeedbackService(self.db)

        overview = await overview_service.get_learning_overview(
            user_id, time_window_days=time_window_days
        )
        knowledge_mastery = await ability_service.get_knowledge_mastery(
            user_id, time_window_days=time_window_days
        )
        weak_points = await ability_service.get_weak_points(
            user_id, time_window_days=time_window_days
        )
        suggestions = await ability_service.get_learning_suggestions(user_id)
        feedback = await feedback_service.generate_feedback(user_id)

        return {
            "overview": overview,
            "ability": {
                "knowledge_mastery": knowledge_mastery,
                "weak_points": weak_points,
                "suggestions": suggestions,
            },
            "feedback": feedback,
        }
    
    # ==================== 辅助方法 ====================
    
    def _admin_to_response(self, admin: Admin) -> AdminInfoResponse:
        """将Admin模型转换为响应"""
        return AdminInfoResponse(
            id=str(admin.id),
            name=admin.name,
            phone=admin.phone,
            email=admin.email,
            is_active=admin.is_active,
            created_at=admin.created_at,
            last_login_at=admin.last_login_at
        )
    
    def _user_to_detail_response(self, user: User) -> UserDetailResponse:
        """将User模型转换为详情响应"""
        return UserDetailResponse(
            id=str(user.id),
            phone=user.phone,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            gender=user.gender.value,
            birthday=user.birthday,
            status=user.status.value,
            disabled_reason=getattr(user, "disabled_reason", None),
            disabled_at=getattr(user, "disabled_at", None),
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
