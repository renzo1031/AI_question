"""
题目服务
提供题目创建、查询等业务逻辑
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.common.question_utils import calculate_content_hash, normalize_question_content
from app.models.question import Question
from app.repositories.question_repo import QuestionRepository
from app.schemas.question import (
    QuestionCreateSchema,
    QuestionListResponseSchema,
    QuestionQuerySchema,
    QuestionResponseSchema,
)


class QuestionService:
    """题目服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.question_repo = QuestionRepository(db)
    
    async def create_question(self, data: QuestionCreateSchema) -> QuestionResponseSchema:
        """
        创建题目
        
        职责：
        1. 题干标准化
        2. 计算 content_hash
        3. 创建题目及关联数据（options、tags）
        4. 控制事务
        5. 处理并发重复插入（通过数据库唯一约束）
        """
        # 1. 题干标准化（使用公共工具函数）
        normalized_content = normalize_question_content(data.content)
        
        # 2. 计算 content_hash（使用公共工具函数）
        content_hash = calculate_content_hash(normalized_content)
        
        # 3. 验证标签是否存在（在事务外先验证，减少事务时间）
        if data.tag_ids:
            await self.question_repo.validate_tags(data.tag_ids)
        
        # 4. 创建题目（在显式事务中）
        # 检查是否已有活动事务，如果有则使用现有事务，否则开启新事务
        # SQLAlchemy 2.0 的 AsyncSession 使用 in_transaction() 检查
        if self.db.in_transaction():
            # 如果已有事务，直接执行操作（不开启新事务）
            return await self._create_question_in_transaction(
                normalized_content, content_hash, data
            )
        else:
            # 如果没有事务，开启新事务
            async with self.db.begin():
                return await self._create_question_in_transaction(
                    normalized_content, content_hash, data
                )
    
    async def _create_question_in_transaction(
        self,
        normalized_content: str,
        content_hash: str,
        data: QuestionCreateSchema
    ) -> QuestionResponseSchema:
        """
        在事务中创建题目的内部方法
        
        注意：此方法假设已经在事务中，不会开启新事务
        """
        try:
            # 创建题目（如果 content_hash 已存在，会抛出 IntegrityError）
            question = await self.question_repo.create(
                content=normalized_content,
                content_hash=content_hash,
                question_type=data.question_type,
                subject=data.subject,
                difficulty=data.difficulty,
                source=data.source,
                ai_answer=data.ai_answer,
                ai_analysis=data.ai_analysis,
                grade=data.grade,
                knowledge_point=data.knowledge_point,
                grade_id=data.grade_id,
                subject_id=data.subject_id,
                knowledge_point_id=data.knowledge_point_id
            )
            
            # 创建选项（通过 Repository）
            if data.options:
                options_data = [
                    {
                        "option_key": opt.option_key,
                        "option_text": opt.option_text
                    }
                    for opt in data.options
                ]
                await self.question_repo.create_options(question.id, options_data)
            
            # 关联标签（通过 Repository）
            if data.tag_ids:
                await self.question_repo.create_tags(question.id, data.tag_ids)
            
            # 在事务内部加载完整数据（包含关联）
            # 使用 selectinload 确保关联数据被加载
            # 重新查询完整数据（在事务内）
            result = await self.db.execute(
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.sub_knowledge_points),
                    selectinload(Question.grade_obj),
                    selectinload(Question.subject_obj),
                    selectinload(Question.knowledge_point_obj)
                )
                .where(Question.id == question.id)
            )
            question = result.scalar_one()
            
        except IntegrityError as e:
            # 处理唯一约束冲突（content_hash 重复）
            if "content_hash" in str(e.orig) or "unique constraint" in str(e.orig).lower():
                # 在事务内重新查询已存在的题目
                existing_question = await self.question_repo.get_by_content_hash(
                    content_hash, load_options=True, load_tags=True
                )
                if existing_question:
                    # 如果找到已存在的题目，直接返回它（不抛出异常）
                    # 这样调用者就不需要处理重复的情况
                    question = existing_question
                else:
                    # 如果查询不到，说明是其他原因导致的重复，抛出异常
                    raise AppException(
                        code=ErrorCode.DB_DUPLICATE,
                        message="题目已存在，无法重复创建"
                    )
            else:
                raise AppException(
                    code=ErrorCode.DB_ERROR,
                    message=f"创建题目失败: {str(e)}"
                )
        except Exception as e:
            if isinstance(e, AppException):
                raise
            raise AppException(
                code=ErrorCode.DB_ERROR,
                message=f"创建题目失败: {str(e)}"
            )
        
        # 返回结果
        return QuestionResponseSchema.model_validate(question)
    
    async def get_question_by_id(self, question_id: int) -> QuestionResponseSchema:
        """根据ID获取题目"""
        question = await self.question_repo.get_by_id(
            question_id, load_options=True, load_tags=True
        )
        if not question:
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message="题目不存在"
            )
        
        return QuestionResponseSchema.model_validate(question)
    
    async def list_questions(self, query: QuestionQuerySchema) -> QuestionListResponseSchema:
        """获取题目列表"""
        questions, total = await self.question_repo.list(
            page=query.page,
            page_size=query.page_size,
            question_id=query.question_id,
            question_type=query.question_type,
            subject=query.subject,
            difficulty=query.difficulty,
            source=query.source,
            tag_id=query.tag_id,
            keyword=query.keyword,
            load_options=True,
            load_tags=True
        )
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size if total > 0 else 0
        
        return QuestionListResponseSchema(
            items=[QuestionResponseSchema.model_validate(q) for q in questions],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    

