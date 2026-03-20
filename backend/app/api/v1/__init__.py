# API v1版本
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_question_bank import router as admin_question_bank_router
from app.api.v1.admin_dashboard import router as admin_dashboard_router
from app.api.v1.admin_announcement import router as admin_announcement_router
from app.api.v1.admin_grade_knowledge import router as admin_grade_knowledge_router
from app.api.v1.admin_system_config import router as admin_system_config_router
from app.api.v1.admin_operation_logs import router as admin_operation_logs_router
from app.api.v1.announcement import router as announcement_router
from app.api.v1.question import router as question_router
from app.api.v1.practice import router as practice_router
from app.api.v1.wrongbook import router as wrongbook_router
from app.api.v1.learning_analysis import router as learning_analysis_router
from app.api.v1.correction import router as correction_router
from app.api.v1.admin_correction import router as admin_correction_router
from app.api.v1.banner import router as banner_router
from app.api.v1.admin_banner import router as admin_banner_router

# 创建v1路由器
router = APIRouter(prefix="/v1")

# 注册子路由
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(admin_router)
router.include_router(admin_question_bank_router)
router.include_router(admin_dashboard_router)
router.include_router(admin_announcement_router)
router.include_router(admin_grade_knowledge_router)
router.include_router(admin_system_config_router)
router.include_router(admin_operation_logs_router)
router.include_router(announcement_router)
router.include_router(question_router)
router.include_router(practice_router)
router.include_router(wrongbook_router)
router.include_router(learning_analysis_router)
router.include_router(correction_router)
router.include_router(admin_correction_router)
router.include_router(banner_router)
router.include_router(admin_banner_router)

