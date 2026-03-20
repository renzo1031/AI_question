"""
练习系统API路由
提供练习出题和答案校验接口
"""
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import get_db
from app.core.security.openapi import jwt_security
from app.middleware.auth import get_current_user_id
from app.schemas.practice import (
    PracticeAnswerSchema,
    PracticeCheckResultSchema,
    PracticeGenerateSchema,
)
from app.services.practice_service import PracticeService

# 创建练习路由
router = APIRouter(prefix="/practice", tags=["练习"])


@router.post("/generate", summary="生成练习题", dependencies=[Depends(jwt_security)])
async def generate_practice_questions(
    request: PracticeGenerateSchema,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    生成练习题
    
    根据学科、年级、章节、知识点等条件生成练习题。
    优先从题库查询，如果数量不足则调用AI生成。
    
    - **subject**: 学科（必填，如：数学、语文）
    - **grade**: 年级（可选，如：七年级、八年级）
    - **chapter**: 章节（可选，如：第一章、第二章）
    - **knowledge_point**: 知识点（可选）
    - **question_type**: 题目类型（可选，如：选择题、填空题）
    - **difficulty**: 难度等级（可选，1-5）
    - **count**: 题目数量（默认10，最大100）
    
    返回练习题列表，包含题目ID、内容、类型、难度、选项和标签。
    """
    practice_service = PracticeService(db)
    questions = await practice_service.generate_practice_questions(user_id, request)
    
    return success(
        data=questions,
        message="生成练习题成功"
    )


@router.post(
    "/questions/{question_id}/answer",
    summary="提交答案并校验",
    dependencies=[Depends(jwt_security)]
)
async def check_practice_answer(
    question_id: int = Path(..., description="题目ID"),
    answer_data: PracticeAnswerSchema = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    提交答案并校验
    
    校验用户提交的答案是否正确，返回正确答案和解析。
    暂不记录错题（后续接入错题功能）。
    
    - **question_id**: 题目ID（路径参数）
    - **answer**: 用户答案（请求体）
    
    返回校验结果，包含：
    - **is_correct**: 是否正确
    - **correct_answer**: 正确答案
    - **analysis**: 题目解析
    """
    practice_service = PracticeService(db)
    result = await practice_service.check_and_record_answer(
        user_id=user_id,
        question_id=question_id,
        user_answer=answer_data.answer
    )
    
    return success(
        data=PracticeCheckResultSchema(**result),
        message="答案校验完成"
    )

