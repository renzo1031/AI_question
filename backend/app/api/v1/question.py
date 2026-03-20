"""
搜题和题库API路由
提供OCR识别、AI解题和题库管理接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import page_success, success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.middleware.auth import get_current_user_id
from app.schemas.question import (
    AvailableProvidersResponse,
    QuestionCreateSchema,
    QuestionQuerySchema,
    SolveQuestionFromImageRequest,
    SolveQuestionFromTextRequest,
    SolveQuestionResponse,
)
from app.services.question import QuestionService
from app.services.question_service import QuestionService as QuestionBankService

# 搜题相关路由
router = APIRouter(prefix="/question", tags=["搜题"])

# 题库相关路由
questions_router = APIRouter(prefix="/questions", tags=["题库"])


@router.post("/solve/image", summary="从图片识别并解题（自动入库）", dependencies=[Depends(jwt_security)])
async def solve_question_from_image(
    request: SolveQuestionFromImageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    从图片识别题目并解题（自动入库到题库）
    
    - **image_url**: 图片URL（与image_base64二选一）
    - **image_base64**: 图片Base64编码（与image_url二选一）
    - **ai_provider**: AI提供商（tongyi/deepseek/kimi），不填使用默认（已废弃，使用统一AI服务）
    - **context**: 上下文信息（可选）
    
    注意：此接口会自动将题目入库，返回结果包含 question_id
    """
    service = QuestionService(db)
    result = await service.solve_question_from_image(
        image_url=request.image_url,
        image_base64=request.image_base64,
        ai_provider=request.ai_provider,
        context=request.context,
        auto_save=True,  # 自动入库
        source="图片识别"
    )
    
    # 如果已入库，返回包含 question_id 的响应
    if result.get("saved"):
        return success(
            data={
                "question": result["question"],
                "answer": result["answer"],
                "question_id": result["question_id"],
                "saved": True
            },
            message="解题成功并已入库"
        )
    else:
        # 兼容旧格式（未入库的情况）
        return success(
            data=SolveQuestionResponse(
                question=result["question"],
                answer=result["answer"]
            ).model_dump(mode="json"),
            message="解题成功"
        )


@router.post("/solve/image/upload", summary="上传图片识别并解题（自动入库）", dependencies=[Depends(jwt_security)])
async def solve_question_from_upload(
    file: UploadFile = File(..., description="题目图片"),
    ai_provider: Optional[str] = Form(None, description="AI提供商（tongyi/deepseek/kimi，已废弃）"),
    context: Optional[str] = Form(None, description="上下文信息（可选）"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    上传图片识别题目并解题（自动入库到题库）
    
    - **file**: 题目图片文件
    - **ai_provider**: AI提供商（已废弃，使用统一AI服务）
    - **context**: 上下文信息（可选）
    
    注意：此接口会自动将题目入库，返回结果包含 question_id
    """
    # 读取文件内容（二进制数据）
    image_bytes = await file.read()
    
    service = QuestionService(db)
    result = await service.solve_question_from_image(
        image_bytes=image_bytes,
        ai_provider=ai_provider,
        context=context,
        auto_save=True,  # 自动入库
        source="图片上传"
    )
    
    # 如果已入库，返回包含 question_id 的响应
    if result.get("saved"):
        return success(
            data={
                "question": result["question"],
                "answer": result["answer"],
                "question_id": result["question_id"],
                "saved": True
            },
            message="解题成功并已入库"
        )
    else:
        # 兼容旧格式（未入库的情况）
        return success(
            data=SolveQuestionResponse(
                question=result["question"],
                answer=result["answer"]
            ).model_dump(mode="json"),
            message="解题成功"
        )


@router.post("/solve/text", summary="从文本解题（自动入库）", dependencies=[Depends(jwt_security)])
async def solve_question_from_text(
    request: SolveQuestionFromTextRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    直接解题（不需要OCR，自动入库到题库）
    
    - **question_text**: 题目文本
    - **ai_provider**: AI提供商（tongyi/deepseek/kimi），不填使用默认（已废弃，使用统一AI服务）
    - **context**: 上下文信息（可选）
    
    注意：此接口会自动将题目入库，返回结果包含 question_id
    """
    service = QuestionService(db)
    result = await service.solve_question_from_text(
        question_text=request.question_text,
        ai_provider=request.ai_provider,
        context=request.context,
        auto_save=True,  # 自动入库
        source="文本输入"
    )
    
    # 如果已入库，返回包含 question_id 的响应
    if result.get("saved"):
        return success(
            data={
                "question": result["question"],
                "answer": result["answer"],
                "question_id": result["question_id"],
                "saved": True
            },
            message="解题成功并已入库"
        )
    else:
        # 兼容旧格式（未入库的情况）
        return success(
            data=SolveQuestionResponse(
                question=result["question"],
                answer=result["answer"]
            ).model_dump(mode="json"),
            message="解题成功"
        )


@router.get("/providers", summary="获取可用的AI提供商列表", dependencies=[Depends(jwt_security)])
async def get_available_providers(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前配置的可用AI提供商列表
    """
    service = QuestionService(db)
    providers = service.get_available_ai_providers()
    return success(
        data=AvailableProvidersResponse(providers=providers).model_dump(mode="json")
    )


# ==================== 题库相关API ====================

@questions_router.post("", summary="创建题目", dependencies=[Depends(jwt_security)])
async def create_question(
    request: QuestionCreateSchema,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    创建题目
    
    - **content**: 题目内容（必填）
    - **question_type**: 题目类型（可选）
    - **subject**: 科目（可选）
    - **difficulty**: 难度等级 1-10（可选）
    - **source**: 来源（可选）
    - **ai_answer**: AI答案（可选）
    - **ai_analysis**: AI解析（可选）
    - **options**: 题目选项列表（可选）
    - **tag_ids**: 标签ID列表（可选）
    
    需要JWT Token认证
    """
    service = QuestionBankService(db)
    question = await service.create_question(request)
    return success(
        data=question.model_dump(mode="json"),
        message="题目创建成功"
    )


@questions_router.get("/{question_id}", summary="获取题目详情", dependencies=[Depends(jwt_security)])
async def get_question(
    question_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取题目详情
    
    - **question_id**: 题目ID
    
    需要JWT Token认证
    """
    service = QuestionBankService(db)
    question = await service.get_question_by_id(question_id)
    return success(data=question.model_dump(mode="json"))


@questions_router.get("", summary="获取题目列表", dependencies=[Depends(jwt_security)])
async def list_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    question_id: Optional[int] = Query(None, description="题目ID筛选"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    difficulty: Optional[int] = Query(None, ge=1, le=10, description="难度等级筛选"),
    source: Optional[str] = Query(None, description="来源筛选"),
    tag_id: Optional[int] = Query(None, description="标笾ID筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（搜索题目内容）"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取题目列表（支持条件过滤和分页）
    
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **question_id**: 题目ID筛选（可选）
    - **question_type**: 题目类型筛选（可选）
    - **subject**: 科目筛选（可选）
    - **difficulty**: 难度等级筛选 1-10（可选）
    - **source**: 来源筛选（可选）
    - **tag_id**: 标笾ID筛选（可选）
    - **keyword**: 关键词搜索（可选）
    
    需要JWT Token认证
    """
    query = QuestionQuerySchema(
        page=page,
        page_size=page_size,
        question_id=question_id,
        question_type=question_type,
        subject=subject,
        difficulty=difficulty,
        source=source,
        tag_id=tag_id,
        keyword=keyword
    )
    
    service = QuestionBankService(db)
    result = await service.list_questions(query)
    
    return page_success(
        data=[item.model_dump(mode="json") for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
        message="获取成功"
    )

