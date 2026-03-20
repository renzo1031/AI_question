from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.common.question_utils import calculate_content_hash, normalize_question_content
from app.models.question import Question
from app.models.question_tag import QuestionTag
from app.repositories.question_repo import QuestionRepository
from app.repositories.tag_repo import TagRepository
from app.schemas.question import (
    QuestionCreateSchema,
    QuestionImportRequestSchema,
    QuestionListResponseSchema,
    QuestionQuerySchema,
    QuestionResponseSchema,
    QuestionUpdateSchema,
    TagCreateSchema,
    TagSchema,
    TagUpdateSchema,
)


class AdminQuestionBankService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.question_repo = QuestionRepository(db)
        self.tag_repo = TagRepository(db)

    async def list_questions(self, query: QuestionQuerySchema) -> QuestionListResponseSchema:
        questions, total = await self.question_repo.list(
            page=query.page,
            page_size=query.page_size,
            question_id=query.question_id,
            question_type=query.question_type,
            subject=query.subject,
            difficulty=query.difficulty,
            source=query.source,
            grade=query.grade,
            knowledge_point=query.knowledge_point,
            tag_id=query.tag_id,
            keyword=query.keyword,
            load_options=True,
            load_tags=True,
        )
        total_pages = (total + query.page_size - 1) // query.page_size if total > 0 else 0
        return QuestionListResponseSchema(
            items=[QuestionResponseSchema.model_validate(q) for q in questions],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
        )

    async def get_question(self, question_id: int) -> QuestionResponseSchema:
        question = await self.question_repo.get_by_id(question_id, load_options=True, load_tags=True)
        if not question:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="题目不存在")
        return QuestionResponseSchema.model_validate(question)

    async def create_question(self, data: QuestionCreateSchema) -> QuestionResponseSchema:
        normalized_content = normalize_question_content(data.content)
        content_hash = calculate_content_hash(normalized_content)

        if data.tag_ids:
            await self.question_repo.validate_tags(data.tag_ids)

        try:
            question = await self.question_repo.create(
                content=normalized_content,
                content_hash=content_hash,
                question_type=data.question_type,
                subject=data.subject,
                difficulty=data.difficulty,
                source=data.source,
                grade=data.grade,
                knowledge_point=data.knowledge_point,
                ai_answer=data.ai_answer,
                ai_analysis=data.ai_analysis,
            )

            if data.options:
                options_data = [
                    {"option_key": opt.option_key, "option_text": opt.option_text}
                    for opt in data.options
                ]
                await self.question_repo.create_options(question.id, options_data)

            if data.tag_ids:
                await self.question_repo.create_tags(question.id, data.tag_ids)

            await self.db.commit()
            
            result = await self.db.execute(
                select(Question)
                .options(selectinload(Question.options), selectinload(Question.sub_knowledge_points))
                .where(Question.id == question.id)
            )
            question = result.scalar_one()
            return QuestionResponseSchema.model_validate(question)

        except IntegrityError as e:
            await self.db.rollback()
            if "content_hash" in str(e.orig) or "unique constraint" in str(e.orig).lower():
                existing = await self.question_repo.get_by_content_hash(
                    content_hash, load_options=True, load_tags=True
                )
                if existing:
                    return QuestionResponseSchema.model_validate(existing)
                raise AppException(code=ErrorCode.DB_DUPLICATE, message="题目已存在")
            raise AppException(code=ErrorCode.DB_ERROR, message=f"创建题目失败: {str(e)}")

    async def update_question(self, question_id: int, data: QuestionUpdateSchema) -> QuestionResponseSchema:
        question = await self.question_repo.get_by_id(question_id, load_options=False, load_tags=False)
        if not question:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="题目不存在")

        values = {}
        if data.content is not None:
            normalized_content = normalize_question_content(data.content)
            values["content"] = normalized_content
            values["content_hash"] = calculate_content_hash(normalized_content)
        if data.question_type is not None:
            values["question_type"] = data.question_type
        if data.subject is not None:
            values["subject"] = data.subject
        if data.difficulty is not None:
            values["difficulty"] = data.difficulty
        if data.source is not None:
            values["source"] = data.source
        if data.grade is not None:
            values["grade"] = data.grade
        if data.knowledge_point is not None:
            values["knowledge_point"] = data.knowledge_point
        if data.ai_answer is not None:
            values["ai_answer"] = data.ai_answer
        if data.ai_analysis is not None:
            values["ai_analysis"] = data.ai_analysis

        if data.tag_ids is not None:
            await self.question_repo.validate_tags(data.tag_ids)

        if values:
            await self.question_repo.update_fields(question_id, **values)

        if data.options is not None:
            await self.question_repo.replace_options(
                question_id,
                [
                    {"option_key": opt.option_key, "option_text": opt.option_text}
                    for opt in data.options
                ],
            )

        if data.tag_ids is not None:
            await self.question_repo.replace_tags(question_id, data.tag_ids)

        await self.db.commit()
        
        result = await self.db.execute(
            select(Question)
            .options(selectinload(Question.options), selectinload(Question.sub_knowledge_points))
            .where(Question.id == question_id)
        )
        return QuestionResponseSchema.model_validate(result.scalar_one())

    async def delete_question(self, question_id: int) -> bool:
        question = await self.question_repo.get_by_id(question_id, load_options=False, load_tags=False)
        if not question:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="题目不存在")

        await self.question_repo.delete(question_id)
        await self.db.commit()
        return True

    async def import_questions(self, request: QuestionImportRequestSchema) -> dict:
        created = 0
        existed = 0
        failed = 0
        errors: list[dict] = []

        for idx, item in enumerate(request.items):
            try:
                before = None
                if item.content:
                    content_hash = calculate_content_hash(normalize_question_content(item.content))
                    before = await self.question_repo.get_by_content_hash(content_hash, load_options=False, load_tags=False)
                res = await self.create_question(item)
                if before is not None and res.content_hash == before.content_hash:
                    existed += 1
                else:
                    created += 1
            except Exception as e:
                failed += 1
                errors.append({"index": idx, "error": str(e)})

        return {"created": created, "existed": existed, "failed": failed, "errors": errors}

    async def export_questions(self, query: QuestionQuerySchema) -> list[dict]:
        result = await self.list_questions(query)
        return [item.model_dump(mode="json") for item in result.items]

    async def list_tags(self, page: int = 1, page_size: int = 20, keyword: Optional[str] = None) -> tuple[list[TagSchema], int]:
        tags, total = await self.tag_repo.list(page=page, page_size=page_size, keyword=keyword)
        return [TagSchema.model_validate(t) for t in tags], total

    async def get_tag(self, tag_id: int) -> TagSchema:
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="标签不存在")
        return TagSchema.model_validate(tag)

    async def create_tag(self, data: TagCreateSchema) -> TagSchema:
        existing = await self.tag_repo.get_by_name(data.name)
        if existing:
            raise AppException(code=ErrorCode.DB_DUPLICATE, message="标签已存在")
        tag = await self.tag_repo.create(
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
            level=data.level,
        )
        return TagSchema.model_validate(tag)

    async def update_tag(self, tag_id: int, data: TagUpdateSchema) -> TagSchema:
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="标签不存在")

        if data.name is not None:
            existing = await self.tag_repo.get_by_name(data.name)
            if existing and existing.id != tag_id:
                raise AppException(code=ErrorCode.DB_DUPLICATE, message="标签名称已存在")

        updated = await self.tag_repo.update(
            tag_id,
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
            level=data.level,
        )
        return TagSchema.model_validate(updated)

    async def delete_tag(self, tag_id: int) -> bool:
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="标签不存在")

        await self.db.execute(delete(QuestionTag).where(QuestionTag.tag_id == tag_id))
        ok = await self.tag_repo.delete(tag_id)
        await self.db.commit()
        return ok
