"""
用户-题目关系服务
提供用户答题记录、错题管理、收藏等业务逻辑
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ErrorCode, NotFoundException
from app.common.utils import get_current_time
from app.models.user_question import UserQuestion, UserQuestionStatus
from app.repositories.question_repo import QuestionRepository
from app.repositories.user_question_repo import UserQuestionRepository
from app.schemas.practice import PracticeQuestionSchema


class UserQuestionService:
    """用户-题目关系服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_question_repo = UserQuestionRepository(db)
        self.question_repo = QuestionRepository(db)
    
    async def record_answer(
        self,
        user_id: int,
        question_id: int,
        answer: str,
        is_correct: bool
    ) -> UserQuestion:
        """
        记录答题结果
        
        功能：
        1. 判断答案是否正确
        2. 自动累计错题次数（如果答错）
        3. 更新状态和答题时间
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            answer: 用户答案
            is_correct: 是否正确
            
        Returns:
            更新后的UserQuestion对象
        """
        # 验证题目是否存在
        question = await self.question_repo.get_by_id(
            question_id, load_options=False, load_tags=False
        )
        if not question:
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message="题目不存在"
            )
        
        # 处理答题结果
        if is_correct:
            # 答对了：状态设为correct，错误次数不变（保留历史记录）
            existing = await self.user_question_repo.get_by_user_and_question(
                user_id, question_id, load_question=False
            )
            new_wrong_count = existing.wrong_count if existing else 0
            
            user_question = await self.user_question_repo.create_or_update(
                user_id=user_id,
                question_id=question_id,
                status=UserQuestionStatus.CORRECT,
                wrong_count=new_wrong_count,
                last_answer=answer,
                last_answer_at=get_current_time()
            )
        else:
            # 答错了：使用原子操作增加错误次数并更新状态，避免并发问题
            user_question = await self.user_question_repo.increment_wrong_count(
                user_id=user_id,
                question_id=question_id,
                status=UserQuestionStatus.WRONG,
                last_answer=answer,
                last_answer_at=get_current_time()
            )
        
        return user_question
    
    async def mark_mastered(
        self,
        user_id: int,
        question_id: int
    ) -> UserQuestion:
        """
        标记题目为已掌握
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            
        Returns:
            更新后的UserQuestion对象
        """
        # 验证题目是否存在
        question = await self.question_repo.get_by_id(
            question_id, load_options=False, load_tags=False
        )
        if not question:
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message="题目不存在"
            )
        
        # 获取现有记录（保留错误次数）
        existing = await self.user_question_repo.get_by_user_and_question(
            user_id, question_id, load_question=False
        )
        
        # 更新状态为已掌握
        user_question = await self.user_question_repo.create_or_update(
            user_id=user_id,
            question_id=question_id,
            status=UserQuestionStatus.CORRECT,
            wrong_count=existing.wrong_count if existing else 0
        )
        
        return user_question
    
    async def mark_favorite(
        self,
        user_id: int,
        question_id: int,
        is_favorite: bool = True
    ) -> UserQuestion:
        """
        标记/取消收藏题目
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            is_favorite: 是否收藏（True=收藏，False=取消收藏）
            
        Returns:
            更新后的UserQuestion对象
        """
        # 验证题目是否存在
        question = await self.question_repo.get_by_id(
            question_id, load_options=False, load_tags=False
        )
        if not question:
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message="题目不存在"
            )
        
        # 获取现有记录
        existing = await self.user_question_repo.get_by_user_and_question(
            user_id, question_id, load_question=False
        )
        
        if is_favorite:
            # 收藏：设置为favorite状态，保留其他状态信息
            new_status = UserQuestionStatus.FAVORITE
            new_wrong_count = existing.wrong_count if existing else 0
        else:
            # 取消收藏：如果当前是favorite，则清除状态；否则保持原状态
            if existing and existing.status == UserQuestionStatus.FAVORITE:
                # 如果之前是收藏，取消后根据错误次数决定状态
                if existing.wrong_count > 0:
                    new_status = UserQuestionStatus.WRONG
                else:
                    new_status = UserQuestionStatus.CORRECT
            else:
                # 保持原状态
                new_status = existing.status if existing else None
            new_wrong_count = existing.wrong_count if existing else 0
        
        # 更新记录
        user_question = await self.user_question_repo.create_or_update(
            user_id=user_id,
            question_id=question_id,
            status=new_status,
            wrong_count=new_wrong_count
        )
        
        return user_question
    
    async def record_answer(
        self,
        user_id: int,
        question_id: int,
        user_answer: str,
        is_correct: bool
    ) -> UserQuestion:
        """
        记录答题结果
        
        规则：
        - 若不存在记录：创建
        - 答错：wrong_count += 1；status="wrong"
        - 答对：status="correct"（wrong_count 不清零）
        - 更新 last_answer/last_answer_at
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            user_answer: 用户答案
            is_correct: 是否正确
            
        Returns:
            更新后的UserQuestion对象
        """
        # 验证题目是否存在
        question = await self.question_repo.get_by_id(
            question_id=question_id
        )
        if not question:
            raise NotFoundException(
                code=ErrorCode.QUESTION_NOT_FOUND,
                message="题目不存在"
            )
        
        now = get_current_time()
        
        if is_correct:
            # 答对了：状态设为correct，错误次数不变（保留历史记录）
            existing = await self.user_question_repo.get_by_user_and_question(
                user_id, question_id, load_question=False
            )
            new_wrong_count = existing.wrong_count if existing else 0
            
            user_question = await self.user_question_repo.upsert_user_question(
                user_id=user_id,
                question_id=question_id,
                status=UserQuestionStatus.CORRECT.value,
                wrong_count=new_wrong_count,
                last_answer=user_answer,
                last_answer_at=now
            )
        else:
            # 答错了：使用原子操作增加错误次数并更新状态，避免并发问题
            user_question = await self.user_question_repo.increment_wrong_count(
                user_id=user_id,
                question_id=question_id,
                status=UserQuestionStatus.WRONG,
                last_answer=user_answer,
                last_answer_at=now
            )
        
        return user_question
    
    async def list_wrong_questions_for_practice(
        self,
        user_id: int,
        subject: Optional[str] = None,
        tags_all: list[str] = None,
        difficulty: Optional[int] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list:
        """
        获取错题列表（用于错题再练）
        
        Args:
            user_id: 用户ID
            subject: 学科筛选（可选）
            tags_all: 标签名称列表（AND 匹配，可选）
            difficulty: 难度等级筛选（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            题目列表（Question对象）
        """
        if tags_all is None:
            tags_all = []
        
        wrong_questions = await self.user_question_repo.list_wrong_questions(
            user_id=user_id,
            subject=subject,
            tags_all=tags_all,
            difficulty=difficulty,
            limit=limit,
            offset=offset
        )
        
        # 提取题目对象
        questions = []
        for uq in wrong_questions:
            if uq.question:
                questions.append(uq.question)
        
        return questions
    
    async def list_wrongbook(
        self,
        user_id: int,
        query_schema
    ) -> tuple[list, dict]:
        """
        获取错题本列表
        
        Args:
            user_id: 用户ID
            query_schema: WrongBookQuerySchema 查询条件
            
        Returns:
            (错题列表, 分页信息)
        """
        from app.schemas.wrongbook import WrongBookItemSchema
        
        # 组装 tags_all
        tags_all = []
        if query_schema.grade:
            tags_all.append(query_schema.grade)
        if query_schema.chapter:
            tags_all.append(query_schema.chapter)
        if query_schema.knowledge_point:
            tags_all.append(query_schema.knowledge_point)
        
        # 计算 offset
        offset = (query_schema.page - 1) * query_schema.page_size
        
        # 调用 repo 查询错题列表和总数
        wrong_questions = await self.user_question_repo.list_wrong_questions(
            user_id=user_id,
            subject=query_schema.subject,
            tags_all=tags_all,
            difficulty=query_schema.difficulty,
            limit=query_schema.page_size,
            offset=offset
        )
        
        total = await self.user_question_repo.count_wrong_questions(
            user_id=user_id,
            subject=query_schema.subject,
            tags_all=tags_all,
            difficulty=query_schema.difficulty
        )
        
        # 转换为 WrongBookItemSchema
        items = []
        for uq in wrong_questions:
            # 转换题目信息
            question = uq.question
            if not question:
                continue
                
            question_tags = [skp.name for skp in question.sub_knowledge_points] if question.sub_knowledge_points else []
            
            practice_question = PracticeQuestionSchema(
                id=question.id,
                content=question.content,
                question_type=question.question_type or "",
                difficulty=question.difficulty or 1,
                options=[],  # 如果需要可以加载
                tags=question_tags
            )
            
            item = WrongBookItemSchema(
                question=practice_question,
                wrong_count=uq.wrong_count,
                last_answer=uq.last_answer,
                last_answer_at=uq.last_answer_at
            )
            items.append(item)
        
        # 计算分页信息
        total_pages = (total + query_schema.page_size - 1) // query_schema.page_size if query_schema.page_size > 0 else 0
        page_info = {
            "page": query_schema.page,
            "page_size": query_schema.page_size,
            "total": total,
            "total_pages": total_pages
        }
        
        return items, page_info
    
    async def get_wrong_questions(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[UserQuestion], int]:
        """
        获取用户的错题本（旧方法，保留兼容性）
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            (错题列表, 总数)
        """
        return await self.user_question_repo.list_wrong_questions(
            user_id=user_id,
            page=page,
            page_size=page_size,
            load_question=True
        )
    
    async def get_user_question_status(
        self,
        user_id: int,
        question_id: int
    ) -> Optional[UserQuestion]:
        """
        获取用户对题目的练习状态
        
        扩展点：可用于练习系统判断题目状态
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            
        Returns:
            UserQuestion对象或None
        """
        return await self.user_question_repo.get_by_user_and_question(
            user_id, question_id, load_question=True
        )
    
    # ==================== 扩展点：练习系统相关 ====================
    
    async def get_practice_statistics(
        self,
        user_id: int
    ) -> dict:
        """
        获取用户练习统计（扩展点）
        
        预留接口，用于练习系统统计：
        - 总答题数
        - 正确数/错误数
        - 错题数
        - 收藏数
        - 掌握数
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        # TODO: 实现练习统计逻辑
        # 可以通过聚合查询实现
        return {
            "total_answered": 0,
            "total_correct": 0,
            "total_wrong": 0,
            "wrong_questions_count": 0,
            "favorite_count": 0,
            "mastered_count": 0
        }
    
    async def get_review_questions(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[UserQuestion]:
        """
        获取需要复习的题目（扩展点）
        
        预留接口，用于练习系统的复习功能：
        - 根据错误次数和最后答题时间推荐复习题目
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            需要复习的题目列表
        """
        # TODO: 实现复习推荐逻辑
        # 可以根据错误次数、最后答题时间等算法推荐
        wrong_questions, _ = await self.user_question_repo.list_wrong_questions(
            user_id=user_id,
            page=1,
            page_size=limit,
            load_question=True
        )
        return wrong_questions

