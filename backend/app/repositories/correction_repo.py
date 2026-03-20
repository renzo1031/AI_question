"""
题目纠错数据访问层
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_correction import QuestionCorrection


class CorrectionRepository:
    """纠错记录仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        question_id: int,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> QuestionCorrection:
        """创建纠错记录"""
        correction = QuestionCorrection(
            question_id=question_id,
            user_id=user_id,
            reason=reason,
            status="pending"
        )
        self.db.add(correction)
        await self.db.flush()
        await self.db.refresh(correction)
        return correction
    
    async def get_by_id(self, correction_id: int) -> Optional[QuestionCorrection]:
        """根据ID获取纠错记录"""
        result = await self.db.execute(
            select(QuestionCorrection).where(QuestionCorrection.id == correction_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        question_id: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> tuple[list[QuestionCorrection], int]:
        """获取纠错记录列表"""
        query = select(QuestionCorrection)
        count_query = select(func.count(QuestionCorrection.id))
        
        # 状态筛选
        if status:
            query = query.where(QuestionCorrection.status == status)
            count_query = count_query.where(QuestionCorrection.status == status)
        
        # 题目ID筛选
        if question_id:
            query = query.where(QuestionCorrection.question_id == question_id)
            count_query = count_query.where(QuestionCorrection.question_id == question_id)
        
        # 用户ID筛选
        if user_id:
            query = query.where(QuestionCorrection.user_id == user_id)
            count_query = count_query.where(QuestionCorrection.user_id == user_id)
        
        # 总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(QuestionCorrection.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        corrections = result.scalars().all()
        
        return list(corrections), total
    
    async def update_status(
        self,
        correction_id: int,
        status: str,
        admin_note: Optional[str] = None,
        handled_by: Optional[str] = None
    ) -> Optional[QuestionCorrection]:
        """更新纠错状态"""
        correction = await self.get_by_id(correction_id)
        if not correction:
            return None
        
        correction.status = status
        correction.admin_note = admin_note
        correction.handled_by = handled_by
        correction.handled_at = datetime.now(ZoneInfo("Asia/Shanghai"))
        
        await self.db.flush()
        await self.db.refresh(correction)
        return correction
    
    async def count_by_status(self, status: str) -> int:
        """统计指定状态的纠错记录数量"""
        result = await self.db.execute(
            select(func.count(QuestionCorrection.id)).where(
                QuestionCorrection.status == status
            )
        )
        return result.scalar() or 0
