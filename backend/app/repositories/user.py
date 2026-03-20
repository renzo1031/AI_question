"""
用户数据访问层
提供用户相关的数据库操作
"""
import uuid
from datetime import datetime
from typing import Optional, Union

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import get_current_time
from app.models.user import Admin, User, UserStatus

# UUID 类型别名，支持字符串或 UUID 对象
UUIDType = Union[uuid.UUID, str]


class UserRepository:
    """用户仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        password_hash: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        nickname: str = ""
    ) -> User:
        """创建用户"""
        user = User(
            phone=phone,
            email=email,
            password_hash=password_hash,
            nickname=nickname or self._generate_nickname(phone, email)
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    def _generate_nickname(
        self, 
        phone: Optional[str], 
        email: Optional[str]
    ) -> str:
        """生成默认昵称"""
        if phone:
            return f"用户{phone[-4:]}"
        elif email:
            local = email.split("@")[0]
            return f"用户{local[:4]}"
        return "新用户"
    
    async def get_by_id(self, user_id: UUIDType) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone_or_email(self, account: str) -> Optional[User]:
        """根据手机号或邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(
                or_(User.phone == account, User.email == account)
            )
        )
        return result.scalar_one_or_none()
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否已存在"""
        result = await self.db.execute(
            select(User.id).where(User.phone == phone)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None
    
    async def update(self, user_id: UUIDType, **kwargs) -> Optional[User]:
        """更新用户信息"""
        # 处理datetime时区问题：将aware datetime转换为naive datetime
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, datetime):
                processed_kwargs[key] = get_current_time()
            else:
                processed_kwargs[key] = value
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**processed_kwargs, updated_at=get_current_time())
        )
        await self.db.flush()
        return await self.get_by_id(user_id)
    
    async def update_password(self, user_id: UUIDType, password_hash: str) -> bool:
        """更新密码"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash, updated_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_last_login(self, user_id: UUIDType) -> bool:
        """更新最后登录时间"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_phone(self, user_id: UUIDType, phone: str) -> bool:
        """更新手机号"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(phone=phone, updated_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_email(self, user_id: UUIDType, email: str) -> bool:
        """更新邮箱"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=email, updated_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_status(self, user_id: UUIDType, status: UserStatus) -> bool:
        """更新用户状态"""
        values = {
            "status": status,
            "updated_at": get_current_time(),
        }
        # 仅当禁用时才保留禁用原因与时间；启用/删除时清理
        if status != UserStatus.DISABLED:
            values["disabled_reason"] = None
            values["disabled_at"] = None

        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**values)
        )
        return result.rowcount > 0

    async def disable_user(self, user_id: UUIDType, reason: Optional[str] = None) -> bool:
        """禁用用户（可选原因）"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                status=UserStatus.DISABLED,
                disabled_reason=reason,
                disabled_at=get_current_time(),
                updated_at=get_current_time(),
            )
        )
        return result.rowcount > 0
    
    # ==================== 用户列表查询（管理员使用） ====================
    
    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[UserStatus] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        last_login_from: Optional[datetime] = None,
        last_login_to: Optional[datetime] = None
    ) -> tuple[list[User], int]:
        """获取用户列表"""
        query = select(User)
        count_query = select(func.count(User.id))
        
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                User.phone.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
                User.nickname.ilike(f"%{keyword}%")
            )
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)
        
        # 状态筛选
        if status:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)

        # 创建时间筛选
        if created_from:
            query = query.where(User.created_at >= created_from)
            count_query = count_query.where(User.created_at >= created_from)
        if created_to:
            query = query.where(User.created_at <= created_to)
            count_query = count_query.where(User.created_at <= created_to)

        # 最后登录时间筛选
        if last_login_from:
            query = query.where(User.last_login_at >= last_login_from)
            count_query = count_query.where(User.last_login_at >= last_login_from)
        if last_login_to:
            query = query.where(User.last_login_at <= last_login_to)
            count_query = count_query.where(User.last_login_at <= last_login_to)
        
        # 排除已删除的用户
        query = query.where(User.status != UserStatus.DELETED)
        count_query = count_query.where(User.status != UserStatus.DELETED)
        
        # 总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        users = result.unique().scalars().all()
        
        return list(users), total


class AdminRepository:
    """管理员仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        password_hash: str,
        name: str,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Admin:
        """创建管理员"""
        base_username = username or self._generate_username(phone=phone, email=email)
        base_username = self._normalize_username(base_username)
        # 尽量保证唯一（兜底：加数字后缀）
        candidate = base_username
        suffix = 1
        while await self._exists_by_username(candidate):
            suffix += 1
            candidate = f"{base_username}{suffix}"

        admin = Admin(
            username=candidate,
            password_hash=password_hash,
            name=name,
            phone=phone,
            email=email,
            is_active=True
        )
        self.db.add(admin)
        await self.db.flush()
        await self.db.refresh(admin)
        return admin

    def _generate_username(self, *, phone: Optional[str], email: Optional[str]) -> str:
        if phone:
            return f"admin_{phone[-6:]}"
        if email:
            local = email.split("@")[0]
            local = "".join(ch for ch in local if ch.isalnum() or ch in ("_", "."))
            local = local[:30] if local else "admin"
            return f"admin_{local}"
        return "admin"

    def _normalize_username(self, username: str) -> str:
        cleaned = "".join(ch for ch in username.strip() if ch.isalnum() or ch in ("_", "."))
        cleaned = cleaned[:50]
        return cleaned or "admin"

    async def _exists_by_username(self, username: str) -> bool:
        result = await self.db.execute(
            select(Admin.id).where(Admin.username == username)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_by_id(self, admin_id: UUIDType) -> Optional[Admin]:
        """根据ID获取管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[Admin]:
        """根据手机号获取管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Admin]:
        """根据邮箱获取管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone_or_email(self, account: str) -> Optional[Admin]:
        """根据手机号或邮箱获取管理员"""
        result = await self.db.execute(
            select(Admin).where(
                or_(Admin.phone == account, Admin.email == account)
            )
        )
        return result.scalar_one_or_none()
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否已存在"""
        result = await self.db.execute(
            select(Admin.id).where(Admin.phone == phone)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        result = await self.db.execute(
            select(Admin.id).where(Admin.email == email)
        )
        return result.scalar_one_or_none() is not None
    
    async def update(self, admin_id: UUIDType, **kwargs) -> Optional[Admin]:
        """更新管理员信息"""
        # 处理datetime时区问题：将aware datetime转换为naive datetime
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, datetime):
                processed_kwargs[key] = get_current_time()
            else:
                processed_kwargs[key] = value
        
        await self.db.execute(
            update(Admin)
            .where(Admin.id == admin_id)
            .values(**processed_kwargs, updated_at=get_current_time())
        )
        await self.db.flush()
        return await self.get_by_id(admin_id)
    
    async def update_password(self, admin_id: UUIDType, password_hash: str) -> bool:
        """更新密码"""
        result = await self.db.execute(
            update(Admin)
            .where(Admin.id == admin_id)
            .values(password_hash=password_hash, updated_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_last_login(self, admin_id: UUIDType) -> bool:
        """更新最后登录时间"""
        result = await self.db.execute(
            update(Admin)
            .where(Admin.id == admin_id)
            .values(last_login_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def update_status(self, admin_id: UUIDType, is_active: bool) -> bool:
        """更新管理员状态"""
        result = await self.db.execute(
            update(Admin)
            .where(Admin.id == admin_id)
            .values(is_active=is_active, updated_at=get_current_time())
        )
        return result.rowcount > 0
    
    async def delete(self, admin_id: UUIDType) -> bool:
        """删除管理员"""
        admin = await self.get_by_id(admin_id)
        if admin:
            await self.db.delete(admin)
            return True
        return False
    
    # ==================== 管理员列表查询 ====================
    
    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[list[Admin], int]:
        """获取管理员列表"""
        query = select(Admin)
        count_query = select(func.count(Admin.id))
        
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                Admin.name.ilike(f"%{keyword}%"),
                Admin.phone.ilike(f"%{keyword}%"),
                Admin.email.ilike(f"%{keyword}%")
            )
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)
        
        # 状态筛选
        if is_active is not None:
            query = query.where(Admin.is_active == is_active)
            count_query = count_query.where(Admin.is_active == is_active)
        
        # 总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(Admin.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        admins = result.scalars().all()
        
        return list(admins), total
