"""
FastAPI应用主入口
AI智能学习系统后端
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import router as api_router
from app.common.exceptions import AppException
from app.core.background_tasks import background_task_manager
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.redis import redis_client
from app.middleware.exception_handler import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.logging import UnifiedLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"Starting {settings.app_name}...")
    
    # 初始化数据库
    await init_db()
    logger.info("Database initialized")
    
    # 连接Redis并检测
    await redis_client.connect()
    is_connected, error_msg = await redis_client.check_connection()
    if not is_connected:
        logger.error(f"Redis连接检测失败: {error_msg}")
        logger.warning("应用将继续启动，但Redis相关功能可能不可用")
    else:
        logger.info("Redis连接正常")
    
    # 启动后台任务
    await background_task_manager.start()
    logger.info("Background tasks started")
    
    yield
    
    # 关闭时
    logger.info(f"Shutting down {settings.app_name}...")
    
    # 停止后台任务
    await background_task_manager.stop()
    logger.info("Background tasks stopped")
    
    # 关闭Redis连接
    await redis_client.disconnect()
    logger.info("Redis disconnected")
    
    # 关闭数据库连接
    await close_db()
    logger.info("Database closed")

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        description="以AI解题为入口,以知识点掌握度为核心的智能学习系统",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # 自定义OpenAPI Schema，添加Security Schemes
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        from fastapi.openapi.utils import get_openapi
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # 确保components存在
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        # 添加Security Schemes
        openapi_schema["components"]["securitySchemes"] = {
            "JWT": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Token认证，格式：Bearer {token}"
            },
            "Session": {
                "type": "apiKey",
                "in": "cookie",
                "name": "admin_session",
                "description": "管理员Session Cookie认证"
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求日志中间件
    app.add_middleware(RequestLoggerMiddleware)
    
    # 统一日志中间件（管理员 + 用户）
    app.add_middleware(UnifiedLoggingMiddleware)
    
    # 注册异常处理器
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # 注册路由
    app.include_router(api_router)
    
    # 健康检查
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """健康检查接口，包含数据库和Redis状态"""
        health_status = {
            "status": "healthy",
            "app": settings.app_name,
            "env": settings.app_env,
            "services": {}
        }
        
        # 检查Redis连接
        redis_connected, redis_error = await redis_client.check_connection()
        health_status["services"]["redis"] = {
            "status": "healthy" if redis_connected else "unhealthy",
            "message": "Redis连接正常" if redis_connected else redis_error
        }
        
        # 如果Redis不可用，整体状态设为degraded
        if not redis_connected:
            health_status["status"] = "degraded"
            health_status["message"] = "Redis服务不可用，部分功能可能受影响"
        
        return health_status
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

