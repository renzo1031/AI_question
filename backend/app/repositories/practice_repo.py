"""
练习数据访问层
提供从题库中按条件查询练习题的功能
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.question import Question
from app.models.question_tag import QuestionTag
from app.models.tag import SubKnowledgePoint


class PracticeRepository:
    """练习仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_questions_by_filters(
        self,
        subject: str,
        tags_all: list[str],
        question_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        limit: int = 10
    ) -> list[Question]:
        """
        从题库中按条件查询练习题
        
        查询规则：
        - subject 必须匹配
        - tags_all 使用 AND 匹配：题目必须包含所有指定的标签
        - question_type / difficulty 可选
        - 使用随机排序
        - 返回数量 <= limit
        
        Args:
            subject: 学科（必填）
            tags_all: 标签名称列表（AND 匹配，题目必须包含所有标签）
            question_type: 题目类型（可选）
            difficulty: 难度等级（可选）
            limit: 返回数量限制
            
        Returns:
            题目列表（已加载 options 和 tags）
        """
        # 基础查询
        query = select(Question).where(Question.subject == subject)
        
        # 标签筛选（AND 匹配：题目必须包含所有指定的标签）
        if tags_all:
            # 方法：通过 join 和 group by 实现 AND 匹配
            # 1. join QuestionTag 和 SubKnowledgePoint
            # 2. 筛选标签名称在 tags_all 列表中
            # 3. group by question_id
            # 4. having count(distinct tag.id) = len(tags_all) 确保包含所有标签
            query = query.join(QuestionTag).join(SubKnowledgePoint).where(
                SubKnowledgePoint.name.in_(tags_all)
            ).group_by(Question.id).having(
                func.count(func.distinct(SubKnowledgePoint.id)) == len(tags_all)
            )
        
        # 题目类型筛选
        if question_type:
            query = query.where(Question.question_type == question_type)
        
        # 难度筛选
        if difficulty is not None:
            query = query.where(Question.difficulty == difficulty)
        
        # 加载关联数据（options 和 sub_knowledge_points）
        query = query.options(
            selectinload(Question.options),
            selectinload(Question.sub_knowledge_points)
        )
        
        # 随机排序（PostgreSQL 使用 random()）
        query = query.order_by(func.random())
        
        # 限制返回数量
        query = query.limit(limit)
        
        # 执行查询
        result = await self.db.execute(query)
        questions = result.unique().scalars().all()
        
        return list(questions)
    
    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """
        根据题目ID获取题目
        
        Args:
            question_id: 题目ID
            
        Returns:
            题目对象（已加载 options 和 tags），如果不存在返回 None
        """
        query = select(Question).where(Question.id == question_id)
        
        # 加载关联数据（options 和 sub_knowledge_points）
        query = query.options(
            selectinload(Question.options),
            selectinload(Question.sub_knowledge_points)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

