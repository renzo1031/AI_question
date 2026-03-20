"""统一日志中间件 - 记录管理员和用户操作"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy import insert

from app.core.database import async_session_factory
from app.models.operation_log import OperationLog, UserType, LogModule


# 管理员日志配置
ADMIN_LOGGED_PATHS = ["/api/v1/admin/"]
ADMIN_EXCLUDED_PATHS = [
    "/api/v1/admin/auth/login",
    "/api/v1/admin/logs",
]

# 用户日志配置
USER_LOGGED_PATHS = [
    "/api/v1/practice/",
    "/api/v1/wrongbook/",
    "/api/v1/learning-analysis/",
    "/api/v1/questions/",
    "/api/v1/announcements/",
]
USER_EXCLUDED_PATHS = [
    "/api/v1/auth/",
]


def get_client_ip(request: Request) -> str:
    """获取客户端真实 IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    if request.client:
        return request.client.host
    
    return "unknown"


def should_log_admin(path: str) -> bool:
    """判断是否需要记录管理员日志"""
    for excluded in ADMIN_EXCLUDED_PATHS:
        if path.startswith(excluded):
            return False
    
    for logged_path in ADMIN_LOGGED_PATHS:
        if path.startswith(logged_path):
            return True
    
    return False


def should_log_user(path: str) -> bool:
    """判断是否需要记录用户日志"""
    for excluded in USER_EXCLUDED_PATHS:
        if path.startswith(excluded):
            return False
    
    for logged_path in USER_LOGGED_PATHS:
        if path.startswith(logged_path):
            return True
    
    return False


def get_action_description(method: str, path: str) -> str:
    """根据请求方法和路径生成中文操作描述"""
    # 路径关键词到中文的映射
    path_mappings = {
        # 认证相关
        "login": "登录",
        "logout": "登出",
        "register": "注册",
        
        # 用户管理
        "users/list": "查看用户列表",
        "users/detail": "查看用户详情",
        "users/status": "更改用户状态",
        "users/password": "重置用户密码",
        
        # 管理员
        "admins/list": "查看管理员列表",
        "admins/create": "创建管理员",
        "/me": "查看个人信息",
        
        # 题目
        "questions/list": "查看题目列表",
        "questions/create": "创建题目",
        "questions/update": "更新题目",
        "questions/delete": "删除题目",
        "questions/batch-delete": "批量删除题目",
        "questions/upload": "上传题目",
        "questions/import": "导入题目",
        "questions/export": "导出题目",
        
        # 公告
        "announcements/list": "查看公告列表",
        "announcements/create": "创建公告",
        "announcements/update": "更新公告",
        "announcements/delete": "删除公告",
        
        # 年级/学科/知识点
        "grades": "管理年级",
        "subjects": "管理学科",
        "knowledge-points": "管理知识点",
        "tags": "管理标签",
        
        # 系统配置
        "system-config/email": "配置邮件",
        "system-config/sms": "配置短信",
        "email/test": "测试邮件",
        "sms/test": "测试短信",
        
        # 日志
        "operation-logs": "查看操作日志",
        "logs/cleanup": "清理旧日志",
        "stats/summary": "查看统计信息",
        
        # 仪表盘
        "dashboard": "查看仪表盘",
        
        # 用户端 - 练习
        "practice/start": "开始练习",
        "practice/submit": "提交答案",
        "practice/history": "查看练习历史",
        
        # 用户端 - 错题本
        "wrongbook": "查看错题本",
        
        # 用户端 - 学习分析
        "learning-analysis": "查看学习分析",
    }
    
    # 默认操作
    method_actions = {
        "GET": "查看",
        "POST": "创建/提交",
        "PUT": "更新",
        "PATCH": "修改",
        "DELETE": "删除",
    }
    
    # 尝试匹配具体路径
    for key, description in path_mappings.items():
        if key in path:
            return description
    
    # 如果没有匹配，使用默认操作
    action = method_actions.get(method, "操作")
    
    # 提取路径中的资源名
    if "/users" in path:
        return f"{action}用户"
    elif "/admins" in path or "/admin" in path:
        return f"{action}管理员信息"
    elif "/questions" in path:
        return f"{action}题目"
    elif "/announcements" in path:
        return f"{action}公告"
    elif "/grades" in path:
        return f"{action}年级"
    elif "/subjects" in path:
        return f"{action}学科"
    elif "/knowledge-points" in path:
        return f"{action}知识点"
    elif "/tags" in path:
        return f"{action}标签"
    elif "/practice" in path:
        return f"{action}练习"
    elif "/wrongbook" in path:
        return f"{action}错题本"
    elif "/learning-analysis" in path or "/analysis" in path:
        return f"{action}学习分析"
    
    return f"{action}资源"


def get_log_module(path: str, is_admin: bool) -> str:
    """根据路径和用户类型推断模块"""
    if "/auth/" in path:
        return LogModule.AUTH
    elif "/users/" in path:
        return LogModule.USER_MANAGE if is_admin else LogModule.OTHER
    elif "/admins/" in path or ("/admin/" in path and is_admin):
        return LogModule.ADMIN
    elif "/questions/" in path or "/question/" in path:
        return LogModule.QUESTION
    elif "/announcements/" in path or "/announcement/" in path:
        return LogModule.ANNOUNCEMENT
    elif "/grades/" in path or "/knowledge-points/" in path or "/subjects/" in path:
        return LogModule.GRADE_KNOWLEDGE
    elif "/system-config/" in path:
        return LogModule.SYSTEM_CONFIG
    elif "/system/" in path:
        return LogModule.SYSTEM
    elif "/practice/" in path:
        return LogModule.PRACTICE
    elif "/wrongbook/" in path:
        return LogModule.WRONGBOOK
    elif "/learning-analysis/" in path or "/analysis/" in path:
        return LogModule.ANALYSIS
    else:
        return LogModule.OTHER


class UnifiedLoggingMiddleware(BaseHTTPMiddleware):
    """统一日志中间件 - 同时处理管理员和用户日志"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        path = request.url.path
        method = request.method
        
        # 判断日志类型
        is_admin_log = should_log_admin(path)
        is_user_log = should_log_user(path)
        
        # 过滤掉 GET 请求，只记录增删改操作
        if method == "GET":
            return await call_next(request)
        
        if not is_admin_log and not is_user_log:
            return await call_next(request)

        # 记录开始时间
        start_time = time.time()

        # 获取用户/管理员信息
        user_id = None
        username = None
        user_type = None
        
        # 管理员：从 Session Cookie 获取
        if is_admin_log:
            from app.core.security.session import session_manager
            session_id = request.cookies.get("admin_session")
            if session_id:
                try:
                    admin_id = await session_manager.get_admin_id(session_id)
                    if admin_id:
                        user_id = admin_id
                        # 从数据库获取管理员信息
                        from app.core.database import get_db
                        async for db in get_db():
                            from app.models.admin import Admin
                            from sqlalchemy import select
                            result = await db.execute(
                                select(Admin).where(Admin.id == admin_id)
                            )
                            admin = result.scalar_one_or_none()
                            if admin:
                                username = admin.username
                            break
                        user_type = "admin"
                except Exception:
                    pass
        
        # 普通用户：从 JWT Token 获取
        elif is_user_log:
            from app.core.security.jwt import jwt_handler
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt_handler.verify_access_token(token)
                    if payload:
                        user_id = payload.get("sub")
                        # 从数据库获取用户信息
                        from app.core.database import get_db
                        async for db in get_db():
                            from app.models.user import User
                            from sqlalchemy import select
                            result = await db.execute(
                                select(User).where(User.id == user_id)
                            )
                            user = result.scalar_one_or_none()
                            if user:
                                username = user.phone
                            break
                        user_type = "user"
                except Exception:
                    pass

        # 获取请求信息
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        request_params = dict(request.query_params) if request.query_params else {}

        # 执行请求
        response = None
        error_message = None
        is_success = True
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            is_success = 200 <= status_code < 400
        except Exception as e:
            error_message = str(e)
            is_success = False
            raise
        finally:
            # 计算响应时间
            response_time_ms = int((time.time() - start_time) * 1000)

            # 推断模块和操作
            module = get_log_module(path, is_admin_log)
            
            # 生成操作描述
            action = get_action_description(method, path)
            
            # 生成描述
            user_desc = username or user_id or "匿名"
            description = f"{user_desc} {action}"

            # 确定日志级别
            if not is_success:
                log_level = "ERROR"
            elif status_code >= 400:
                log_level = "WARNING"
            else:
                log_level = "INFO"

            # 异步记录日志（统一表）
            try:
                async with async_session_factory() as db:
                    await db.execute(
                        insert(OperationLog).values(
                            user_type=UserType.ADMIN if is_admin_log else UserType.USER,
                            user_id=user_id,
                            username=username,
                            log_level=log_level,
                            module=module,
                            action=action,
                            description=description,
                            request_method=method,
                            request_path=path,
                            request_params=request_params,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            status_code=status_code,
                            is_success=is_success,
                            error_message=error_message,
                            response_time_ms=response_time_ms,
                        )
                    )
                    await db.commit()
            except Exception as log_error:
                # 日志记录失败不应影响正常请求
                print(f"Failed to log action: {log_error}")

        return response
