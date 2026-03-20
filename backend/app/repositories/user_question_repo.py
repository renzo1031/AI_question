"""
用户-题目关系数据访问层
提供用户题目练习记录相关的数据库操作
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.question import Question
from app.models.user_question import UserQuestion, UserQuestionStatus


class UserQuestionRepository:
    """用户-题目关系仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_user_and_question(
        self,
        user_id: int,
        question_id: int,
        load_question: bool = True
    ) -> Optional[UserQuestion]:
        """
        根据用户ID和题目ID获取记录
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            load_question: 是否加载题目关联数据
            
        Returns:
            UserQuestion对象或None
        """
        query = select(UserQuestion).where(
            UserQuestion.user_id == user_id,
            UserQuestion.question_id == question_id
        )
        
        # 可选加载题目关联数据
        if load_question:
            query = query.options(selectinload(UserQuestion.question))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_or_update(
        self,
        user_id: int,
        question_id: int,
        status: Optional[UserQuestionStatus] = None,
        wrong_count: Optional[int] = None,
        last_answer: Optional[str] = None,
        last_answer_at: Optional[datetime] = None
    ) -> UserQuestion:
        """
        创建或更新用户-题目关系记录（使用 PostgreSQL ON CONFLICT 避免竞态条件）
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            status: 状态（wrong/correct/favorite）
            wrong_count: 错误次数（如果提供，直接设置该值）
            last_answer: 最后一次答案
            last_answer_at: 最后一次答题时间
            
        Returns:
            创建或更新后的UserQuestion对象
        """
        # 构建更新字典
        update_dict = {}
        if status is not None:
            update_dict["status"] = status
        if wrong_count is not None:
            update_dict["wrong_count"] = wrong_count
        if last_answer is not None:
            update_dict["last_answer"] = last_answer
        if last_answer_at is not None:
            update_dict["last_answer_at"] = last_answer_at
        
        # 使用 PostgreSQL 的 INSERT ... ON CONFLICT DO UPDATE
        # 避免先查询再创建/更新的竞态条件
        values_dict = {
            "user_id": user_id,
            "question_id": question_id,
            "status": status,
            "wrong_count": wrong_count if wrong_count is not None else 0,
            "last_answer": last_answer,
            "last_answer_at": last_answer_at
        }
        
        # 合并更新字典到 values_dict（用于冲突时的更新）
        if update_dict:
            # 构建 ON CONFLICT 更新表达式
            # 只更新非 None 的字段
            update_expr = {k: v for k, v in update_dict.items() if v is not None}
            if not update_expr:
                update_expr = values_dict
            
            stmt = (
                insert(UserQuestion)
                .values(**values_dict)
                .on_conflict_do_update(
                    index_elements=["user_id", "question_id"],
                    set_=update_expr
                )
                .returning(UserQuestion)
            )
        else:
            # 如果没有更新字段，冲突时不做任何操作，直接返回现有记录
            stmt = (
                insert(UserQuestion)
                .values(**values_dict)
                .on_conflict_do_nothing(
                    index_elements=["user_id", "question_id"]
                )
                .returning(UserQuestion)
            )
        
        # 执行并返回结果
        result = await self.db.execute(stmt)
        user_question = result.scalar_one_or_none()
        
        # 如果冲突时没有更新（do_nothing），需要重新查询
        if user_question is None:
            user_question = await self.get_by_user_and_question(
                user_id, question_id, load_question=False
            )
        
        await self.db.flush()
        return user_question
    
    async def increment_wrong_count(
        self,
        user_id: int,
        question_id: int,
        status: Optional[UserQuestionStatus] = None,
        last_answer: Optional[str] = None,
        last_answer_at: Optional[datetime] = None
    ) -> UserQuestion:
        """
        原子性地增加错误次数并更新其他字段（解决并发问题）
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            status: 状态（可选）
            last_answer: 最后一次答案（可选）
            last_answer_at: 最后一次答题时间（可选）
            
        Returns:
            更新后的UserQuestion对象
        """
        # 构建更新字典
        update_values = {"wrong_count": UserQuestion.wrong_count + 1}
        if status is not None:
            update_values["status"] = status
        if last_answer is not None:
            update_values["last_answer"] = last_answer
        if last_answer_at is not None:
            update_values["last_answer_at"] = last_answer_at
        
        # 使用数据库原子操作更新错误次数和其他字段
        stmt = (
            update(UserQuestion)
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.question_id == question_id
            )
            .values(**update_values)
            .returning(UserQuestion)
        )
        
        result = await self.db.execute(stmt)
        updated = result.scalar_one_or_none()
        
        if updated:
            await self.db.flush()
            return updated
        
        # 如果记录不存在，创建新记录
        return await self.create_or_update(
            user_id=user_id,
            question_id=question_id,
            status=status or UserQuestionStatus.WRONG,
            wrong_count=1,
            last_answer=last_answer,
            last_answer_at=last_answer_at
        )
    
    async def upsert_user_question(
        self,
        user_id: int,
        question_id: int,
        *,
        status: str,
        wrong_count: int,
        last_answer: str,
        last_answer_at: datetime
    ) -> UserQuestion:
        """
        创建或更新用户-题目关系记录（使用 PostgreSQL ON CONFLICT 避免竞态条件）
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            status: 状态（wrong/correct/favorite）
            wrong_count: 错误次数
            last_answer: 最后一次答案
            last_answer_at: 最后一次答题时间
            
        Returns:
            创建或更新后的UserQuestion对象
        """
        # 转换 status 字符串为枚举
        status_enum = UserQuestionStatus(status) if isinstance(status, str) else status
        
        values_dict = {
            "user_id": user_id,
            "question_id": question_id,
            "status": status_enum,
            "wrong_count": wrong_count,
            "last_answer": last_answer,
            "last_answer_at": last_answer_at
        }
        
        # 使用 PostgreSQL 的 INSERT ... ON CONFLICT DO UPDATE
        stmt = (
            insert(UserQuestion)
            .values(**values_dict)
            .on_conflict_do_update(
                index_elements=["user_id", "question_id"],
                set_=values_dict
            )
            .returning(UserQuestion)
        )
        
        result = await self.db.execute(stmt)
        user_question = result.scalar_one_or_none()
        
        # 如果冲突时没有更新，需要重新查询
        if user_question is None:
            user_question = await self.get_by_user_and_question(
                user_id, question_id, load_question=False
            )
        
        await self.db.flush()
        return user_question
    
    async def list_wrong_questions(
        self,
        user_id: int,
        subject: Optional[str] = None,
        tags_all: list[str] = None,
        difficulty: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[UserQuestion]:
        """
        获取用户的错题列表（支持按条件筛选）
        
        Args:
            user_id: 用户ID
            subject: 学科筛选（可选）
            tags_all: 标签名称列表（AND 匹配，可选）
            difficulty: 难度等级筛选（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            错题列表（已加载题目关联数据）
        """
        if tags_all is None:
            tags_all = []
        
        # 基础查询：只查询错题
        query = (
            select(UserQuestion)
            .join(Question, UserQuestion.question_id == Question.id)
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.status == UserQuestionStatus.WRONG
            )
        )
        
        # 学科筛选
        if subject:
            query = query.where(Question.subject == subject)
        
        # 难度筛选
        if difficulty is not None:
            query = query.where(Question.difficulty == difficulty)
        
        # 标签筛选（AND 匹配：题目必须包含所有指定的标签）
        if tags_all:
            from app.models.question_tag import QuestionTag
            from app.models.tag import SubKnowledgePoint
            
            query = query.join(QuestionTag, Question.id == QuestionTag.question_id).join(
                SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id
            ).where(
                SubKnowledgePoint.name.in_(tags_all)
            ).group_by(UserQuestion.user_id, UserQuestion.question_id).having(
                func.count(func.distinct(SubKnowledgePoint.id)) == len(tags_all)
            )
        
        # 加载题目关联数据（包含 options 和 sub_knowledge_points）
        query = query.options(
            selectinload(UserQuestion.question).selectinload(Question.options),
            selectinload(UserQuestion.question).selectinload(Question.sub_knowledge_points)
        )
        
        # 排序：按错误次数降序，然后按最后答题时间降序
        query = query.order_by(
            UserQuestion.wrong_count.desc(),
            UserQuestion.last_answer_at.desc().nulls_last()
        )
        
        # 分页
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        user_questions = result.unique().scalars().all()
        
        return list(user_questions)
    
    async def count_wrong_questions(
        self,
        user_id: int,
        subject: Optional[str] = None,
        tags_all: list[str] = None,
        difficulty: Optional[int] = None
    ) -> int:
        """
        统计用户的错题数量（支持按条件筛选）
        
        Args:
            user_id: 用户ID
            subject: 学科筛选（可选）
            tags_all: 标签名称列表（AND 匹配，可选）
            difficulty: 难度等级筛选（可选）
            
        Returns:
            错题总数
        """
        if tags_all is None:
            tags_all = []
        
        # 基础查询：只统计错题
        query = (
            select(func.count(func.distinct(UserQuestion.question_id)))
            .select_from(UserQuestion)
            .join(Question, UserQuestion.question_id == Question.id)
            .where(
                UserQuestion.user_id == user_id,
                UserQuestion.status == UserQuestionStatus.WRONG
            )
        )
        
        # 学科筛选
        if subject:
            query = query.where(Question.subject == subject)
        
        # 难度筛选
        if difficulty is not None:
            query = query.where(Question.difficulty == difficulty)
        
        # 标签筛选（AND 匹配：题目必须包含所有指定的标签）
        if tags_all:
            from app.models.question_tag import QuestionTag
            from app.models.tag import SubKnowledgePoint
            
            query = (
                query.join(QuestionTag, Question.id == QuestionTag.question_id)
                .join(SubKnowledgePoint, QuestionTag.tag_id == SubKnowledgePoint.id)
                .where(SubKnowledgePoint.name.in_(tags_all))
                .group_by(UserQuestion.user_id)
                .having(func.count(func.distinct(SubKnowledgePoint.id)) == len(tags_all))
            )
        
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return count

