# API层：路由和接口定义
from fastapi import APIRouter

from app.api.v1 import router as v1_router

# 创建主路由器
router = APIRouter(prefix="/api")

# 注册版本路由
router.include_router(v1_router)
