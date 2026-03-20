"""
题目数据访问层
提供题目相关的数据库操作
"""
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.question_tag import QuestionTag
from app.models.tag import SubKnowledgePoint


class QuestionRepository:
    """题目仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(
        self, 
        question_id: int,
        load_options: bool = True,
        load_tags: bool = True
    ) -> Optional[Question]:
        """根据ID获取题目"""
        query = select(Question).where(Question.id == question_id)
        
        # 可选加载关联数据
        if load_options:
            query = query.options(selectinload(Question.options))
        if load_tags:
            query = query.options(selectinload(Question.sub_knowledge_points))
        
        # 预加载年级/学科/知识点对象
        query = query.options(
            selectinload(Question.grade_obj),
            selectinload(Question.subject_obj),
            selectinload(Question.knowledge_point_obj)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_content_hash(
        self,
        content_hash: str,
        load_options: bool = True,
        load_tags: bool = True
    ) -> Optional[Question]:
        """根据内容哈希获取题目"""
        query = select(Question).where(Question.content_hash == content_hash)
        
        # 可选加载关联数据
        if load_options:
            query = query.options(selectinload(Question.options))
        if load_tags:
            query = query.options(selectinload(Question.sub_knowledge_points))
        
        # 预加载年级/学科/知识点对象
        query = query.options(
            selectinload(Question.grade_obj),
            selectinload(Question.subject_obj),
            selectinload(Question.knowledge_point_obj)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        content: str,
        content_hash: str,
        question_type: Optional[str] = None,
        subject: Optional[str] = None,
        difficulty: Optional[int] = None,
        source: Optional[str] = None,
        grade: Optional[str] = None,
        knowledge_point: Optional[str] = None,
        ai_answer: Optional[str] = None,
        ai_analysis: Optional[str] = None,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None
    ) -> Question:
        """
        创建题目
        
        注意：如果 content_hash 已存在，会抛出 IntegrityError
        """
        question = Question(
            content=content,
            content_hash=content_hash,
            question_type=question_type,
            subject=subject,
            difficulty=difficulty,
            source=source,
            grade=grade,
            knowledge_point=knowledge_point,
            ai_answer=ai_answer,
            ai_analysis=ai_analysis,
            grade_id=grade_id,
            subject_id=subject_id,
            knowledge_point_id=knowledge_point_id
        )
        self.db.add(question)
        await self.db.flush()
        # 不需要 refresh，因为 flush 后对象已经有 id
        return question
    
    async def create_options(
        self,
        question_id: int,
        options: list[dict]
    ) -> list[QuestionOption]:
        """
        创建题目选项
        
        Args:
            question_id: 题目ID
            options: 选项列表，每个选项包含 option_key 和 option_text
            
        Returns:
            创建的选项列表
        """
        option_objects = []
        for option_data in options:
            option = QuestionOption(
                question_id=question_id,
                option_key=option_data["option_key"],
                option_text=option_data["option_text"]
            )
            self.db.add(option)
            option_objects.append(option)
        
        await self.db.flush()
        return option_objects

    async def replace_options(self, question_id: int, options: list[dict]) -> list[QuestionOption]:
        """替换题目选项（先删后建）"""
        await self.db.execute(
            delete(QuestionOption).where(QuestionOption.question_id == question_id)
        )
        await self.db.flush()
        if not options:
            return []
        return await self.create_options(question_id, options)
    
    async def create_tags(
        self,
        question_id: int,
        tag_ids: list[int]
    ) -> list[QuestionTag]:
        """
        关联题目标签
        
        Args:
            question_id: 题目ID
            tag_ids: 标签ID列表
            
        Returns:
            创建的关联记录列表
        """
        tag_objects = []
        for tag_id in tag_ids:
            question_tag = QuestionTag(
                question_id=question_id,
                tag_id=tag_id
            )
            self.db.add(question_tag)
            tag_objects.append(question_tag)
        
        await self.db.flush()
        return tag_objects

    async def replace_tags(self, question_id: int, tag_ids: list[int]) -> list[QuestionTag]:
        """替换题目标签（先删后建）"""
        await self.db.execute(
            delete(QuestionTag).where(QuestionTag.question_id == question_id)
        )
        await self.db.flush()
        if not tag_ids:
            return []
        return await self.create_tags(question_id, tag_ids)

    async def update_fields(self, question_id: int, **kwargs) -> bool:
        """更新题目字段"""
        if not kwargs:
            return True
        result = await self.db.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(**kwargs)
        )
        return result.rowcount > 0

    async def delete(self, question_id: int) -> bool:
        """删除题目（同时清理关联）"""
        await self.db.execute(
            delete(QuestionTag).where(QuestionTag.question_id == question_id)
        )
        await self.db.execute(
            delete(QuestionOption).where(QuestionOption.question_id == question_id)
        )
        result = await self.db.execute(
            delete(Question).where(Question.id == question_id)
        )
        return result.rowcount > 0
    
    async def validate_tags(self, tag_ids: list[int]) -> None:
        """
        验证标签ID是否存在
        
        Args:
            tag_ids: 标签ID列表
            
        Returns:
            None，如果标签不存在会抛出异常
        """
        if not tag_ids:
            return
        
        result = await self.db.execute(
            select(SubKnowledgePoint.id).where(SubKnowledgePoint.id.in_(tag_ids))
        )
        existing_tag_ids = set(result.scalars().all())
        
        missing_tag_ids = set(tag_ids) - existing_tag_ids
        if missing_tag_ids:
            from app.common.exceptions import NotFoundException, ErrorCode
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message=f"标签不存在: {', '.join(map(str, missing_tag_ids))}"
            )
    
    async def get_or_create_tags_by_names(self, tag_names: list[str]) -> list[int]:
        """
        根据标签名称获取或创建标签，返回标签ID列表
        
        Args:
            tag_names: 标签名称列表
            
        Returns:
            标签ID列表（按输入顺序）
        """
        if not tag_names:
            return []
        
        # 去重但保持顺序
        unique_names = []
        seen = set()
        for name in tag_names:
            if name and name.strip() and name not in seen:
                unique_names.append(name.strip())
                seen.add(name.strip())
        
        if not unique_names:
            return []
        
        # 查询已存在的标签
        result = await self.db.execute(
            select(SubKnowledgePoint).where(SubKnowledgePoint.name.in_(unique_names))
        )
        existing_tags = {tag.name: tag.id for tag in result.scalars().all()}
        
        # 创建不存在的标签
        tag_ids = []
        for name in unique_names:
            if name in existing_tags:
                tag_ids.append(existing_tags[name])
            else:
                # 创建新标签
                new_tag = SubKnowledgePoint(name=name)
                self.db.add(new_tag)
                await self.db.flush()
                await self.db.refresh(new_tag)
                tag_ids.append(new_tag.id)
                existing_tags[name] = new_tag.id
        
        return tag_ids
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        question_id: Optional[int] = None,
        question_type: Optional[str] = None,
        subject: Optional[str] = None,
        difficulty: Optional[int] = None,
        source: Optional[str] = None,
        grade: Optional[str] = None,
        knowledge_point: Optional[str] = None,
        tag_id: Optional[int] = None,
        keyword: Optional[str] = None,
        load_options: bool = True,
        load_tags: bool = True
    ) -> tuple[list[Question], int]:
        """获取题目列表（支持条件过滤和分页）"""
        query = select(Question)
        count_query = select(func.count(Question.id))
        
        # 题目ID筛选
        if question_id is not None:
            query = query.where(Question.id == question_id)
            count_query = count_query.where(Question.id == question_id)
        
        # 标签筛选（通过关联表）
        if tag_id is not None:
            query = query.join(QuestionTag).where(QuestionTag.tag_id == tag_id)
            count_query = count_query.join(QuestionTag).where(QuestionTag.tag_id == tag_id)
        
        # 题目类型筛选
        if question_type:
            query = query.where(Question.question_type == question_type)
            count_query = count_query.where(Question.question_type == question_type)
        
        # 科目筛选
        if subject:
            query = query.where(Question.subject == subject)
            count_query = count_query.where(Question.subject == subject)
        
        # 难度筛选
        if difficulty is not None:
            query = query.where(Question.difficulty == difficulty)
            count_query = count_query.where(Question.difficulty == difficulty)
        
        # 来源筛选
        if source:
            query = query.where(Question.source == source)
            count_query = count_query.where(Question.source == source)
        
        # 年级筛选
        if grade:
            query = query.where(Question.grade == grade)
            count_query = count_query.where(Question.grade == grade)
        
        # 知识点筛选
        if knowledge_point:
            query = query.where(Question.knowledge_point == knowledge_point)
            count_query = count_query.where(Question.knowledge_point == knowledge_point)
        
        # 关键词搜索（搜索题目内容）
        if keyword:
            keyword_filter = Question.content.ilike(f"%{keyword}%")
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)
        
        # 加载关联数据
        if load_options:
            query = query.options(selectinload(Question.options))
        if load_tags:
            query = query.options(selectinload(Question.sub_knowledge_points))
        
        # 预加载年级/学科/知识点对象
        query = query.options(
            selectinload(Question.grade_obj),
            selectinload(Question.subject_obj),
            selectinload(Question.knowledge_point_obj)
        )
        
        # 总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(Question.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        questions = result.unique().scalars().all()
        
        return list(questions), total

