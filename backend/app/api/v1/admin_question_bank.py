from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.question import (
    QuestionCreateSchema,
    QuestionImportRequestSchema,
    QuestionQuerySchema,
    QuestionUpdateSchema,
    TagCreateSchema,
    TagUpdateSchema,
)
from app.services.admin_question_bank_service import AdminQuestionBankService


router = APIRouter(prefix="/admin/question-bank", tags=["管理端题库"])


@router.get("/questions", summary="管理端-题目列表", dependencies=[Depends(session_security)])
async def admin_list_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    question_id: Optional[int] = Query(None, description="题目ID筛选"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    difficulty: Optional[int] = Query(None, ge=1, le=10, description="难度筛选"),
    source: Optional[str] = Query(None, description="来源筛选"),
    tag_id: Optional[int] = Query(None, description="标签ID筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    query = QuestionQuerySchema(
        page=page,
        page_size=page_size,
        question_id=question_id,
        question_type=question_type,
        subject=subject,
        difficulty=difficulty,
        source=source,
        tag_id=tag_id,
        keyword=keyword,
    )
    service = AdminQuestionBankService(db)
    result = await service.list_questions(query)
    return page_success(
        data=[item.model_dump(mode="json") for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
        message="获取成功",
    )


@router.get("/questions/{question_id}", summary="管理端-题目详情", dependencies=[Depends(session_security)])
async def admin_get_question(
    question_id: int,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    question = await service.get_question(question_id)
    return success(data=question.model_dump(mode="json"))


@router.post("/questions", summary="管理端-创建题目", dependencies=[Depends(session_security)])
async def admin_create_question(
    request: QuestionCreateSchema,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    question = await service.create_question(request)
    return success(data=question.model_dump(mode="json"), message="创建成功")


@router.put("/questions/{question_id}", summary="管理端-更新题目", dependencies=[Depends(session_security)])
async def admin_update_question(
    question_id: int,
    request: QuestionUpdateSchema,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    question = await service.update_question(question_id, request)
    return success(data=question.model_dump(mode="json"), message="更新成功")


@router.delete("/questions/{question_id}", summary="管理端-删除题目", dependencies=[Depends(session_security)])
async def admin_delete_question(
    question_id: int,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    await service.delete_question(question_id)
    return success(message="删除成功")


@router.post("/questions/import", summary="管理端-批量导入题目", dependencies=[Depends(session_security)])
async def admin_import_questions(
    request: QuestionImportRequestSchema,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    result = await service.import_questions(request)
    return success(data=result, message="导入完成")


@router.get("/questions/export", summary="管理端-导出题目（JSON）", dependencies=[Depends(session_security)])
async def admin_export_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=500, description="每页数量"),
    question_id: Optional[int] = Query(None, description="题目ID筛选"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    difficulty: Optional[int] = Query(None, ge=1, le=10, description="难度筛选"),
    source: Optional[str] = Query(None, description="来源筛选"),
    tag_id: Optional[int] = Query(None, description="标笾ID筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    query = QuestionQuerySchema(
        page=page,
        page_size=page_size,
        question_id=question_id,
        question_type=question_type,
        subject=subject,
        difficulty=difficulty,
        source=source,
        tag_id=tag_id,
        keyword=keyword,
    )
    service = AdminQuestionBankService(db)
    items = await service.export_questions(query)
    return success(data={"items": items})


@router.get("/tags", summary="管理端-标签列表", dependencies=[Depends(session_security)])
async def admin_list_tags(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    tags, total = await service.list_tags(page=page, page_size=page_size, keyword=keyword)
    return page_success(
        data=[t.model_dump(mode="json") for t in tags],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.get("/tags/{tag_id}", summary="管理端-标签详情", dependencies=[Depends(session_security)])
async def admin_get_tag(
    tag_id: int,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    tag = await service.get_tag(tag_id)
    return success(data=tag.model_dump(mode="json"))


@router.post("/tags", summary="管理端-创建标签", dependencies=[Depends(session_security)])
async def admin_create_tag(
    request: TagCreateSchema,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    tag = await service.create_tag(request)
    return success(data=tag.model_dump(mode="json"), message="创建成功")


@router.put("/tags/{tag_id}", summary="管理端-更新标签", dependencies=[Depends(session_security)])
async def admin_update_tag(
    tag_id: int,
    request: TagUpdateSchema,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    tag = await service.update_tag(tag_id, request)
    return success(data=tag.model_dump(mode="json"), message="更新成功")


@router.delete("/tags/{tag_id}", summary="管理端-删除标签", dependencies=[Depends(session_security)])
async def admin_delete_tag(
    tag_id: int,
    admin_id: int = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = AdminQuestionBankService(db)
    await service.delete_tag(tag_id)
    return success(message="删除成功")
