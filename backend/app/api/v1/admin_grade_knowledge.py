"""
管理端年级和知识点 API
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import session_security
from app.middleware.auth import get_current_admin_id
from app.schemas.grade_knowledge import (
    GradeCreateSchema,
    GradeUpdateSchema,
    KnowledgePointCreateSchema,
    KnowledgePointUpdateSchema,
    SubjectCreateSchema,
    SubjectUpdateSchema,
)
from app.services.grade_knowledge_service import GradeKnowledgeService


router = APIRouter(prefix="/admin/grade-knowledge", tags=["管理端年级知识点"])


# ==================== 年级管理 ====================

@router.get("/grades", summary="管理端-年级列表", dependencies=[Depends(session_security)])
async def list_grades(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    with_subjects: bool = Query(False, description="是否包含学科列表"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取年级列表
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **keyword**: 关键词搜索（可选）
    - **with_subjects**: 是否包含学科列表（可选）
    - **with_knowledge_points**: 是否包含学科及知识点列表（可选）
    """
    service = GradeKnowledgeService(db)
    grades, total = await service.list_grades(
        page=page,
        page_size=page_size,
        keyword=keyword,
        with_subjects=with_subjects,
        with_knowledge_points=with_knowledge_points
    )
    return page_success(
        data=[g.model_dump(mode="json") for g in grades],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功"
    )


@router.get("/grades/all", summary="管理端-所有年级（不分页）", dependencies=[Depends(session_security)])
async def list_all_grades(
    with_subjects: bool = Query(False, description="是否包含学科列表"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有年级（不分页）
    
    - **with_subjects**: 是否包含学科列表（可选）
    - **with_knowledge_points**: 是否包含学科及知识点列表（可选）
    """
    service = GradeKnowledgeService(db)
    grades = await service.list_all_grades(with_subjects=with_subjects, with_knowledge_points=with_knowledge_points)
    return success(data=[g.model_dump(mode="json") for g in grades])


@router.get("/grades/{grade_id}", summary="管理端-年级详情", dependencies=[Depends(session_security)])
async def get_grade(
    grade_id: int,
    with_subjects: bool = Query(False, description="是否包含学科列表"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取年级详情
    
    - **grade_id**: 年级ID
    - **with_subjects**: 是否包含学科列表（可选）
    - **with_knowledge_points**: 是否包含学科及知识点列表（可选）
    """
    service = GradeKnowledgeService(db)
    grade = await service.get_grade(grade_id, with_subjects=with_subjects, with_knowledge_points=with_knowledge_points)
    return success(data=grade.model_dump(mode="json"))


@router.post("/grades", summary="管理端-创建年级", dependencies=[Depends(session_security)])
async def create_grade(
    request: GradeCreateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    创建年级
    
    - **name**: 年级名称（必填）
    - **description**: 年级描述（可选）
    - **sort_order**: 排序（可选，默认0）
    """
    service = GradeKnowledgeService(db)
    grade = await service.create_grade(request)
    return success(data=grade.model_dump(mode="json"), message="创建成功")


@router.put("/grades/{grade_id}", summary="管理端-更新年级", dependencies=[Depends(session_security)])
async def update_grade(
    grade_id: int,
    request: GradeUpdateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    更新年级
    
    - **grade_id**: 年级ID
    - **name**: 年级名称（可选）
    - **description**: 年级描述（可选）
    - **sort_order**: 排序（可选）
    """
    service = GradeKnowledgeService(db)
    grade = await service.update_grade(grade_id, request)
    return success(data=grade.model_dump(mode="json"), message="更新成功")


@router.delete("/grades/{grade_id}", summary="管理端-删除年级", dependencies=[Depends(session_security)])
async def delete_grade(
    grade_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    删除年级
    
    - **grade_id**: 年级ID
    
    注意：删除年级会级联删除其下所有知识点
    """
    service = GradeKnowledgeService(db)
    await service.delete_grade(grade_id)
    return success(message="删除成功")


# ==================== 学科管理 ====================

@router.get("/subjects", summary="管理端-学科列表", dependencies=[Depends(session_security)])
async def list_subjects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=200, description="每页数量"),
    grade_id: Optional[int] = Query(None, description="年级ID筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    with_grade: bool = Query(False, description="是否包含年级信息"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    subjects, total = await service.list_subjects(
        page=page,
        page_size=page_size,
        grade_id=grade_id,
        keyword=keyword,
        with_grade=with_grade,
        with_knowledge_points=with_knowledge_points,
    )
    return page_success(
        data=[s.model_dump(mode="json") for s in subjects],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.get("/grades/{grade_id}/subjects", summary="管理端-指定年级的学科列表", dependencies=[Depends(session_security)])
async def list_subjects_by_grade(
    grade_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=200, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    subjects, total = await service.list_subjects_by_grade(
        grade_id=grade_id,
        page=page,
        page_size=page_size,
        keyword=keyword,
        with_knowledge_points=with_knowledge_points,
    )
    return page_success(
        data=[s.model_dump(mode="json") for s in subjects],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.get("/subjects/{subject_id}", summary="管理端-学科详情", dependencies=[Depends(session_security)])
async def get_subject(
    subject_id: int,
    with_grade: bool = Query(False, description="是否包含年级信息"),
    with_knowledge_points: bool = Query(False, description="是否包含知识点列表"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    subject = await service.get_subject(
        subject_id,
        with_grade=with_grade,
        with_knowledge_points=with_knowledge_points,
    )
    return success(data=subject.model_dump(mode="json"))


@router.post("/subjects", summary="管理端-创建学科", dependencies=[Depends(session_security)])
async def create_subject(
    request: SubjectCreateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    subject = await service.create_subject(request)
    return success(data=subject.model_dump(mode="json"), message="创建成功")


@router.put("/subjects/{subject_id}", summary="管理端-更新学科", dependencies=[Depends(session_security)])
async def update_subject(
    subject_id: int,
    request: SubjectUpdateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    subject = await service.update_subject(subject_id, request)
    return success(data=subject.model_dump(mode="json"), message="更新成功")


@router.delete("/subjects/{subject_id}", summary="管理端-删除学科", dependencies=[Depends(session_security)])
async def delete_subject(
    subject_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    await service.delete_subject(subject_id)
    return success(message="删除成功")


# ==================== 知识点管理 ====================

@router.get("/knowledge-points", summary="管理端-知识点列表", dependencies=[Depends(session_security)])
async def list_knowledge_points(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=200, description="每页数量"),
    grade_id: Optional[int] = Query(None, description="年级ID筛选"),
    subject_id: Optional[int] = Query(None, description="学科ID筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    with_subject: bool = Query(False, description="是否包含学科信息"),
    with_grade: bool = Query(False, description="是否包含年级信息"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取知识点列表
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **grade_id**: 年级ID筛选（可选）
    - **subject_id**: 学科ID筛选（可选）
    - **keyword**: 关键词搜索（可选）
    - **with_subject**: 是否包含学科信息（可选）
    - **with_grade**: 是否包含年级信息（可选）
    """
    service = GradeKnowledgeService(db)
    kps, total = await service.list_knowledge_points(
        page=page,
        page_size=page_size,
        grade_id=grade_id,
        subject_id=subject_id,
        keyword=keyword,
        with_subject=with_subject,
        with_grade=with_grade
    )
    return page_success(
        data=[kp.model_dump(mode="json") for kp in kps],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功"
    )



@router.get("/subjects/{subject_id}/knowledge-points", summary="管理端-指定学科的知识点列表", dependencies=[Depends(session_security)])
async def list_knowledge_points_by_subject(
    subject_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=200, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    service = GradeKnowledgeService(db)
    kps, total = await service.list_knowledge_points_by_subject(
        subject_id=subject_id,
        page=page,
        page_size=page_size,
        keyword=keyword,
    )
    return page_success(
        data=[kp.model_dump(mode="json") for kp in kps],
        page=page,
        page_size=page_size,
        total=total,
        message="获取成功",
    )


@router.get("/knowledge-points/{kp_id}", summary="管理端-知识点详情", dependencies=[Depends(session_security)])
async def get_knowledge_point(
    kp_id: int,
    with_subject: bool = Query(False, description="是否包含学科信息"),
    with_grade: bool = Query(False, description="是否包含年级信息"),
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取知识点详情
    
    - **kp_id**: 知识点ID
    - **with_subject**: 是否包含学科信息（可选）
    - **with_grade**: 是否包含年级信息（可选）
    """
    service = GradeKnowledgeService(db)
    kp = await service.get_knowledge_point(kp_id, with_subject=with_subject, with_grade=with_grade)
    return success(data=kp.model_dump(mode="json"))


@router.post("/knowledge-points", summary="管理端-创建知识点", dependencies=[Depends(session_security)])
async def create_knowledge_point(
    request: KnowledgePointCreateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    创建知识点
    
    - **name**: 知识点名称（必填）
    - **subject_id**: 所属学科ID（必填）
    - **description**: 知识点描述（可选）
    - **sort_order**: 排序（可选，默认0）
    """
    service = GradeKnowledgeService(db)
    kp = await service.create_knowledge_point(request)
    return success(data=kp.model_dump(mode="json"), message="创建成功")


@router.put("/knowledge-points/{kp_id}", summary="管理端-更新知识点", dependencies=[Depends(session_security)])
async def update_knowledge_point(
    kp_id: int,
    request: KnowledgePointUpdateSchema,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    更新知识点
    
    - **kp_id**: 知识点ID
    - **name**: 知识点名称（可选）
    - **subject_id**: 所属学科ID（可选）
    - **description**: 知识点描述（可选）
    - **sort_order**: 排序（可选）
    """
    service = GradeKnowledgeService(db)
    kp = await service.update_knowledge_point(kp_id, request)
    return success(data=kp.model_dump(mode="json"), message="更新成功")


@router.delete("/knowledge-points/{kp_id}", summary="管理端-删除知识点", dependencies=[Depends(session_security)])
async def delete_knowledge_point(
    kp_id: int,
    admin_id: str = Depends(get_current_admin_id),
    db: AsyncSession = Depends(get_db),
):
    """
    删除知识点
    
    - **kp_id**: 知识点ID
    """
    service = GradeKnowledgeService(db)
    await service.delete_knowledge_point(kp_id)
    return success(message="删除成功")
