from typing import List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import SubKnowledgePoint


class TagRepository:
    """次知识点仓储类（原标签仓储）"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, tag_id: int) -> Optional[SubKnowledgePoint]:
        result = await self.db.execute(select(SubKnowledgePoint).where(SubKnowledgePoint.id == tag_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[SubKnowledgePoint]:
        result = await self.db.execute(select(SubKnowledgePoint).where(SubKnowledgePoint.name == name))
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        knowledge_point_id: Optional[int] = None,
        sort_order: int = 0,
    ) -> SubKnowledgePoint:
        tag = SubKnowledgePoint(
            name=name,
            description=description,
            knowledge_point_id=knowledge_point_id,
            sort_order=sort_order,
        )
        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def update(
        self,
        tag_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        knowledge_point_id: Optional[int] = None,
        sort_order: Optional[int] = None,
    ) -> Optional[SubKnowledgePoint]:
        values = {}
        if name is not None:
            values["name"] = name
        if description is not None:
            values["description"] = description
        if knowledge_point_id is not None:
            values["knowledge_point_id"] = knowledge_point_id
        if sort_order is not None:
            values["sort_order"] = sort_order

        if values:
            await self.db.execute(
                update(SubKnowledgePoint).where(SubKnowledgePoint.id == tag_id).values(**values)
            )
            await self.db.flush()

        return await self.get_by_id(tag_id)

    async def delete(self, tag_id: int) -> bool:
        tag = await self.get_by_id(tag_id)
        if not tag:
            return False
        await self.db.delete(tag)
        return True

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        knowledge_point_id: Optional[int] = None,
    ) -> Tuple[List[SubKnowledgePoint], int]:
        query = select(SubKnowledgePoint)
        count_query = select(func.count(SubKnowledgePoint.id))

        if keyword:
            query = query.where(SubKnowledgePoint.name.ilike(f"%{keyword}%"))
            count_query = count_query.where(SubKnowledgePoint.name.ilike(f"%{keyword}%"))
        
        if knowledge_point_id is not None:
            query = query.where(SubKnowledgePoint.knowledge_point_id == knowledge_point_id)
            count_query = count_query.where(SubKnowledgePoint.knowledge_point_id == knowledge_point_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(SubKnowledgePoint.sort_order.asc(), SubKnowledgePoint.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total
