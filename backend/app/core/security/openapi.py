"""
OpenAPI Security定义
用于Swagger文档中的认证配置
"""
from fastapi.security import HTTPBearer, APIKeyCookie

# JWT认证（用于普通用户接口）
jwt_security = HTTPBearer(
    scheme_name="JWT",
    description="JWT Token认证，格式：Bearer {token}",
    auto_error=False
)

# Session Cookie认证（用于管理员接口）
session_security = APIKeyCookie(
    name="admin_session",
    scheme_name="Session",
    description="管理员Session Cookie认证",
    auto_error=False
)

