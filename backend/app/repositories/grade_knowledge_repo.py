"""
年级、学科、知识点仓储层
"""
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.grade_knowledge import Grade, KnowledgePoint, Subject


class GradeRepository:
    """年级仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(
        self,
        grade_id: int,
        load_subjects: bool = False,
        load_subjects_knowledge_points: bool = False,
    ) -> Optional[Grade]:
        """根据ID获取年级"""
        query = select(Grade).where(Grade.id == grade_id)
        if load_subjects or load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects))
        if load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects).selectinload(Subject.knowledge_points))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Grade]:
        """根据名称获取年级"""
        result = await self.db.execute(
            select(Grade).where(Grade.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        load_subjects: bool = False,
        load_subjects_knowledge_points: bool = False,
    ) -> Tuple[List[Grade], int]:
        """获取年级列表"""
        query = select(Grade)
        count_query = select(func.count(Grade.id))
        
        if keyword:
            condition = or_(
                Grade.name.ilike(f"%{keyword}%"),
                Grade.description.ilike(f"%{keyword}%")
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        
        # 获取总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 排序和分页
        query = query.order_by(Grade.sort_order.asc(), Grade.id.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        if load_subjects or load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects))
        if load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects).selectinload(Subject.knowledge_points))
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def list_all(self, load_subjects: bool = False, load_subjects_knowledge_points: bool = False) -> List[Grade]:
        """获取所有年级"""
        query = select(Grade).order_by(Grade.sort_order.asc(), Grade.id.asc())
        if load_subjects or load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects))
        if load_subjects_knowledge_points:
            query = query.options(selectinload(Grade.subjects).selectinload(Subject.knowledge_points))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        sort_order: int = 0
    ) -> Grade:
        """创建年级"""
        grade = Grade(
            name=name,
            description=description,
            sort_order=sort_order
        )
        self.db.add(grade)
        await self.db.flush()
        await self.db.refresh(grade)
        return grade
    
    async def update(
        self,
        grade_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: Optional[int] = None
    ) -> Optional[Grade]:
        """更新年级"""
        grade = await self.get_by_id(grade_id)
        if not grade:
            return None
        
        if name is not None:
            grade.name = name
        if description is not None:
            grade.description = description
        if sort_order is not None:
            grade.sort_order = sort_order
        
        await self.db.flush()
        await self.db.refresh(grade)
        return grade
    
    async def delete(self, grade_id: int) -> bool:
        """删除年级"""
        grade = await self.get_by_id(grade_id)
        if not grade:
            return False
        await self.db.delete(grade)
        return True


class KnowledgePointRepository:
    """知识点仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(
        self,
        kp_id: int,
        load_subject: bool = False,
        load_grade: bool = False,
    ) -> Optional[KnowledgePoint]:
        """根据ID获取知识点"""
        query = select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
        if load_subject:
            query = query.options(selectinload(KnowledgePoint.subject))
        if load_grade:
            query = query.options(selectinload(KnowledgePoint.subject).selectinload(Subject.grade))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name_and_subject(self, name: str, subject_id: int) -> Optional[KnowledgePoint]:
        """根据名称和学科获取知识点"""
        result = await self.db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.name == name,
                KnowledgePoint.subject_id == subject_id
            )
        )
        return result.scalar_one_or_none()
    

    async def list_by_subject(
        self,
        subject_id: int,
        page: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
    ) -> Tuple[List[KnowledgePoint], int]:
        """获取指定学科的知识点列表"""
        query = select(KnowledgePoint).where(KnowledgePoint.subject_id == subject_id)
        count_query = select(func.count(KnowledgePoint.id)).where(KnowledgePoint.subject_id == subject_id)
        
        if keyword:
            condition = or_(
                KnowledgePoint.name.ilike(f"%{keyword}%"),
                KnowledgePoint.description.ilike(f"%{keyword}%")
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(KnowledgePoint.sort_order.asc(), KnowledgePoint.id.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 100,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        keyword: Optional[str] = None,
        load_subject: bool = False,
        load_grade: bool = False,
    ) -> Tuple[List[KnowledgePoint], int]:
        """获取知识点列表"""
        query = select(KnowledgePoint)
        count_query = select(func.count(KnowledgePoint.id))
        
        if grade_id is not None:
            query = query.join(Subject).where(Subject.grade_id == grade_id)
            count_query = count_query.join(Subject).where(Subject.grade_id == grade_id)
        
        if subject_id is not None:
            query = query.where(KnowledgePoint.subject_id == subject_id)
            count_query = count_query.where(KnowledgePoint.subject_id == subject_id)
        
        if keyword:
            condition = or_(
                KnowledgePoint.name.ilike(f"%{keyword}%"),
                KnowledgePoint.description.ilike(f"%{keyword}%")
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        
        # 获取总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 排序和分页
        query = query.order_by(KnowledgePoint.sort_order.asc(), KnowledgePoint.id.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        if load_subject:
            query = query.options(selectinload(KnowledgePoint.subject))
        if load_grade:
            query = query.options(selectinload(KnowledgePoint.subject).selectinload(Subject.grade))
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def create(
        self,
        name: str,
        subject_id: int,
        description: Optional[str] = None,
        sort_order: int = 0
    ) -> KnowledgePoint:
        """创建知识点"""
        kp = KnowledgePoint(
            name=name,
            subject_id=subject_id,
            description=description,
            sort_order=sort_order
        )
        self.db.add(kp)
        await self.db.flush()
        await self.db.refresh(kp)
        return kp
    
    async def update(
        self,
        kp_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        subject_id: Optional[int] = None,
        sort_order: Optional[int] = None
    ) -> Optional[KnowledgePoint]:
        """更新知识点"""
        kp = await self.get_by_id(kp_id)
        if not kp:
            return None
        
        if name is not None:
            kp.name = name
        if description is not None:
            kp.description = description
        if subject_id is not None:
            kp.subject_id = subject_id
        if sort_order is not None:
            kp.sort_order = sort_order
        
        await self.db.flush()
        await self.db.refresh(kp)
        return kp
    
    async def delete(self, kp_id: int) -> bool:
        """删除知识点"""
        kp = await self.get_by_id(kp_id)
        if not kp:
            return False
        await self.db.delete(kp)
        return True


class SubjectRepository:
    """学科仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(
        self,
        subject_id: int,
        load_knowledge_points: bool = False,
        load_grade: bool = False,
    ) -> Optional[Subject]:
        """根据ID获取学科"""
        query = select(Subject).where(Subject.id == subject_id)
        if load_knowledge_points:
            query = query.options(selectinload(Subject.knowledge_points))
        if load_grade:
            query = query.options(selectinload(Subject.grade))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name_and_grade(self, name: str, grade_id: int) -> Optional[Subject]:
        """根据名称和年级获取学科"""
        result = await self.db.execute(
            select(Subject).where(
                Subject.name == name,
                Subject.grade_id == grade_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 100,
        grade_id: Optional[int] = None,
        keyword: Optional[str] = None,
        load_grade: bool = False,
        load_knowledge_points: bool = False,
    ) -> Tuple[List[Subject], int]:
        """获取学科列表"""
        query = select(Subject)
        count_query = select(func.count(Subject.id))
        
        if grade_id is not None:
            query = query.where(Subject.grade_id == grade_id)
            count_query = count_query.where(Subject.grade_id == grade_id)
        
        if keyword:
            condition = or_(
                Subject.name.ilike(f"%{keyword}%"),
                Subject.description.ilike(f"%{keyword}%"),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(Subject.sort_order.asc(), Subject.id.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        if load_grade:
            query = query.options(selectinload(Subject.grade))
        if load_knowledge_points:
            query = query.options(selectinload(Subject.knowledge_points))
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def list_by_grade(
        self,
        grade_id: int,
        page: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
        load_knowledge_points: bool = False,
    ) -> Tuple[List[Subject], int]:
        """获取指定年级的学科列表"""
        query = select(Subject).where(Subject.grade_id == grade_id)
        count_query = select(func.count(Subject.id)).where(Subject.grade_id == grade_id)
        
        if keyword:
            condition = or_(
                Subject.name.ilike(f"%{keyword}%"),
                Subject.description.ilike(f"%{keyword}%"),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(Subject.sort_order.asc(), Subject.id.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        if load_knowledge_points:
            query = query.options(selectinload(Subject.knowledge_points))
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def create(
        self,
        name: str,
        grade_id: int,
        description: Optional[str] = None,
        sort_order: int = 0,
    ) -> Subject:
        """创建学科"""
        subject = Subject(
            name=name,
            grade_id=grade_id,
            description=description,
            sort_order=sort_order,
        )
        self.db.add(subject)
        await self.db.flush()
        await self.db.refresh(subject)
        return subject
    
    async def update(
        self,
        subject_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        grade_id: Optional[int] = None,
        sort_order: Optional[int] = None,
    ) -> Optional[Subject]:
        """更新学科"""
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None
        
        if name is not None:
            subject.name = name
        if description is not None:
            subject.description = description
        if grade_id is not None:
            subject.grade_id = grade_id
        if sort_order is not None:
            subject.sort_order = sort_order
        
        await self.db.flush()
        await self.db.refresh(subject)
        return subject
    
    async def delete(self, subject_id: int) -> bool:
        """删除学科"""
        subject = await self.get_by_id(subject_id)
        if not subject:
            return False
        await self.db.delete(subject)
        return True
