"""
错题本API路由
提供错题本查询和错题再练接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.middleware.auth import get_current_user_id
from app.schemas.practice import PracticeGenerateSchema
from app.schemas.wrongbook import WrongBookItemSchema, WrongBookQuerySchema
from app.services.practice_service import PracticeService
from app.services.user_question_service import UserQuestionService

# 创建错题本路由
router = APIRouter(prefix="/wrongbook", tags=["错题本"])


@router.get("", summary="获取错题本列表", dependencies=[Depends(jwt_security)])
async def get_wrongbook(
    subject: str | None = Query(None, description="学科筛选"),
    grade: str | None = Query(None, description="年级筛选"),
    chapter: str | None = Query(None, description="章节筛选"),
    knowledge_point: str | None = Query(None, description="知识点筛选"),
    difficulty: int | None = Query(None, ge=1, le=5, description="难度等级筛选（1-5）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取错题本列表
    
    支持按学科、年级、章节、知识点、难度等条件筛选错题。
    
    - **subject**: 学科（可选）
    - **grade**: 年级（可选）
    - **chapter**: 章节（可选）
    - **knowledge_point**: 知识点（可选）
    - **difficulty**: 难度等级（可选，1-5）
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    
    返回错题列表和分页信息。
    """
    query_schema = WrongBookQuerySchema(
        subject=subject,
        grade=grade,
        chapter=chapter,
        knowledge_point=knowledge_point,
        difficulty=difficulty,
        page=page,
        page_size=page_size
    )
    
    user_question_service = UserQuestionService(db)
    items, page_info = await user_question_service.list_wrongbook(user_id, query_schema)
    
    return page_success(
        data=[WrongBookItemSchema.model_validate(item) for item in items],
        page=page_info["page"],
        page_size=page_info["page_size"],
        total=page_info["total"],
        message="获取错题本成功"
    )


@router.post("/practice/generate", summary="错题再练", dependencies=[Depends(jwt_security)])
async def generate_practice_from_wrongbook(
    request: PracticeGenerateSchema,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    从错题本中生成练习题（错题再练）
    
    出题逻辑：
    1. 优先从 user_question.status=wrong 的题目中抽取
    2. 数量不足时回退到题库查询
    3. 仍不足时调用 AI 补题
    
    - **subject**: 学科（必填）
    - **grade**: 年级（可选）
    - **chapter**: 章节（可选）
    - **knowledge_point**: 知识点（可选）
    - **question_type**: 题目类型（可选）
    - **difficulty**: 难度等级（可选，1-5）
    - **count**: 题目数量（默认10，最大100）
    
    返回练习题列表。
    """
    practice_service = PracticeService(db)
    questions = await practice_service.generate_practice_from_wrongbook(user_id, request)
    
    return success(
        data=questions,
        message="错题再练生成成功"
    )

