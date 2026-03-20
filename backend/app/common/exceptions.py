"""
自定义异常模块
定义业务异常和错误码
"""
from typing import Any, Optional


class ErrorCode:
    """错误码定义"""
    
    # 通用错误 1xxx
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    PARAM_ERROR = 1001
    NOT_FOUND = 1002
    FORBIDDEN = 1003
    TOO_MANY_REQUESTS = 1004
    
    # 认证错误 2xxx
    UNAUTHORIZED = 2001
    TOKEN_EXPIRED = 2002
    TOKEN_INVALID = 2003
    SESSION_EXPIRED = 2004
    SESSION_INVALID = 2005
    
    # 用户错误 3xxx
    USER_NOT_FOUND = 3001
    USER_ALREADY_EXISTS = 3002
    PASSWORD_INCORRECT = 3003
    PHONE_ALREADY_EXISTS = 3004
    EMAIL_ALREADY_EXISTS = 3005
    VERIFY_CODE_INCORRECT = 3006
    VERIFY_CODE_EXPIRED = 3007
    USER_DISABLED = 3008
    
    # 管理员错误 4xxx
    ADMIN_NOT_FOUND = 4001
    ADMIN_ALREADY_EXISTS = 4002
    ADMIN_PASSWORD_INCORRECT = 4003
    ADMIN_DISABLED = 4004
    PERMISSION_DENIED = 4005
    
    # 数据库错误 9xxx
    DB_ERROR = 9001
    DB_DUPLICATE = 9002
    
    # AI错误 8xxx
    AI_SERVICE_ERROR = 8001
    AI_RESPONSE_INVALID = 8002
    AI_JSON_PARSE_ERROR = 8003
    AI_RESPONSE_MISSING_FIELD = 8004


class ErrorMessage:
    """错误消息映射"""
    
    messages = {
        ErrorCode.SUCCESS: "操作成功",
        ErrorCode.UNKNOWN_ERROR: "未知错误",
        ErrorCode.PARAM_ERROR: "参数错误",
        ErrorCode.NOT_FOUND: "资源不存在",
        ErrorCode.FORBIDDEN: "禁止访问",
        ErrorCode.TOO_MANY_REQUESTS: "请求过于频繁",
        
        ErrorCode.UNAUTHORIZED: "未授权",
        ErrorCode.TOKEN_EXPIRED: "Token已过期",
        ErrorCode.TOKEN_INVALID: "Token无效",
        ErrorCode.SESSION_EXPIRED: "Session已过期",
        ErrorCode.SESSION_INVALID: "Session无效",
        
        ErrorCode.USER_NOT_FOUND: "用户不存在",
        ErrorCode.USER_ALREADY_EXISTS: "用户已存在",
        ErrorCode.PASSWORD_INCORRECT: "密码错误",
        ErrorCode.PHONE_ALREADY_EXISTS: "手机号已被注册",
        ErrorCode.EMAIL_ALREADY_EXISTS: "邮箱已被注册",
        ErrorCode.VERIFY_CODE_INCORRECT: "验证码错误",
        ErrorCode.VERIFY_CODE_EXPIRED: "验证码已过期",
        ErrorCode.USER_DISABLED: "用户已被禁用",
        
        ErrorCode.ADMIN_NOT_FOUND: "管理员不存在",
        ErrorCode.ADMIN_ALREADY_EXISTS: "管理员已存在",
        ErrorCode.ADMIN_PASSWORD_INCORRECT: "管理员密码错误",
        ErrorCode.ADMIN_DISABLED: "管理员已被禁用",
        ErrorCode.PERMISSION_DENIED: "权限不足",
        
        ErrorCode.DB_ERROR: "数据库错误",
        ErrorCode.DB_DUPLICATE: "数据重复",
        
        ErrorCode.AI_SERVICE_ERROR: "AI服务异常",
        ErrorCode.AI_RESPONSE_INVALID: "AI返回结果无效",
        ErrorCode.AI_JSON_PARSE_ERROR: "AI返回JSON解析失败",
        ErrorCode.AI_RESPONSE_MISSING_FIELD: "AI返回结果缺少必需字段",
    }
    
    @classmethod
    def get(cls, code: int) -> str:
        return cls.messages.get(code, "未知错误")


class AppException(Exception):
    """
    应用自定义异常基类
    """
    
    def __init__(
        self,
        code: int = ErrorCode.UNKNOWN_ERROR,
        message: Optional[str] = None,
        data: Optional[Any] = None,
        http_status: int = 400
    ):
        self.code = code
        self.message = message or ErrorMessage.get(code)
        self.data = data
        self.http_status = http_status
        super().__init__(self.message)


class AuthException(AppException):
    """认证异常"""
    
    def __init__(
        self,
        code: int = ErrorCode.UNAUTHORIZED,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ):
        super().__init__(code, message, data, http_status=401)


class NotFoundException(AppException):
    """资源不存在异常"""
    
    def __init__(
        self,
        code: int = ErrorCode.NOT_FOUND,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ):
        super().__init__(code, message, data, http_status=404)


class ForbiddenException(AppException):
    """禁止访问异常"""
    
    def __init__(
        self,
        code: int = ErrorCode.FORBIDDEN,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ):
        super().__init__(code, message, data, http_status=403)


class ValidationException(AppException):
    """验证异常"""
    
    def __init__(
        self,
        code: int = ErrorCode.PARAM_ERROR,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ):
        super().__init__(code, message, data, http_status=422)

