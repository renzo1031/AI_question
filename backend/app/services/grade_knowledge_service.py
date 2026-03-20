"""
年级、学科、知识点服务层
"""
from typing import List, Optional, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.repositories.grade_knowledge_repo import GradeRepository, KnowledgePointRepository, SubjectRepository
from app.schemas.grade_knowledge import (
    GradeCreateSchema,
    GradeResponseSchema,
    GradeUpdateSchema,
    GradeWithSubjectsAndKnowledgePointsSchema,
    GradeWithSubjectsSchema,
    SubjectCreateSchema,
    SubjectResponseSchema,
    SubjectUpdateSchema,
    SubjectWithGradeSchema,
    SubjectWithKnowledgePointsSchema,
    KnowledgePointCreateSchema,
    KnowledgePointResponseSchema,
    KnowledgePointUpdateSchema,
    KnowledgePointWithSubjectGradeSchema,
    KnowledgePointWithSubjectSchema,
)


class GradeKnowledgeService:
    """年级、学科、知识点服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.grade_repo = GradeRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.kp_repo = KnowledgePointRepository(db)
    
    # ==================== 年级管理 ====================
    
    async def list_grades(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        with_subjects: bool = False,
        with_knowledge_points: bool = False,
    ) -> Tuple[
        Union[
            List[GradeResponseSchema],
            List[GradeWithSubjectsSchema],
            List[GradeWithSubjectsAndKnowledgePointsSchema],
        ],
        int,
    ]:
        """获取年级列表"""
        load_subjects = with_subjects or with_knowledge_points
        load_subjects_knowledge_points = with_knowledge_points
        grades, total = await self.grade_repo.list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            load_subjects=load_subjects,
            load_subjects_knowledge_points=load_subjects_knowledge_points,
        )
        
        if with_knowledge_points:
            return [GradeWithSubjectsAndKnowledgePointsSchema.model_validate(g) for g in grades], total
        if with_subjects:
            return [GradeWithSubjectsSchema.model_validate(g) for g in grades], total
        return [GradeResponseSchema.model_validate(g) for g in grades], total
    
    async def list_all_grades(
        self,
        with_subjects: bool = False,
        with_knowledge_points: bool = False,
    ) -> Union[
        List[GradeResponseSchema],
        List[GradeWithSubjectsSchema],
        List[GradeWithSubjectsAndKnowledgePointsSchema],
    ]:
        """获取所有年级"""
        load_subjects = with_subjects or with_knowledge_points
        load_subjects_knowledge_points = with_knowledge_points
        grades = await self.grade_repo.list_all(
            load_subjects=load_subjects,
            load_subjects_knowledge_points=load_subjects_knowledge_points,
        )
        
        if with_knowledge_points:
            return [GradeWithSubjectsAndKnowledgePointsSchema.model_validate(g) for g in grades]
        if with_subjects:
            return [GradeWithSubjectsSchema.model_validate(g) for g in grades]
        return [GradeResponseSchema.model_validate(g) for g in grades]
    
    async def get_grade(
        self,
        grade_id: int,
        with_subjects: bool = False,
        with_knowledge_points: bool = False,
    ) -> Union[GradeResponseSchema, GradeWithSubjectsSchema, GradeWithSubjectsAndKnowledgePointsSchema]:
        """获取年级详情"""
        load_subjects = with_subjects or with_knowledge_points
        load_subjects_knowledge_points = with_knowledge_points
        grade = await self.grade_repo.get_by_id(
            grade_id,
            load_subjects=load_subjects,
            load_subjects_knowledge_points=load_subjects_knowledge_points,
        )
        if not grade:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="年级不存在")
        
        if with_knowledge_points:
            return GradeWithSubjectsAndKnowledgePointsSchema.model_validate(grade)
        if with_subjects:
            return GradeWithSubjectsSchema.model_validate(grade)
        return GradeResponseSchema.model_validate(grade)
    
    async def create_grade(self, data: GradeCreateSchema) -> GradeResponseSchema:
        """创建年级"""
        # 检查名称是否已存在
        existing = await self.grade_repo.get_by_name(data.name)
        if existing:
            raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"年级 '{data.name}' 已存在")
        
        grade = await self.grade_repo.create(
            name=data.name,
            description=data.description,
            sort_order=data.sort_order
        )
        await self.db.commit()
        return GradeResponseSchema.model_validate(grade)
    
    async def update_grade(self, grade_id: int, data: GradeUpdateSchema) -> GradeResponseSchema:
        """更新年级"""
        grade = await self.grade_repo.get_by_id(grade_id)
        if not grade:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="年级不存在")
        
        # 如果修改名称，检查是否与其他年级重复
        if data.name is not None and data.name != grade.name:
            existing = await self.grade_repo.get_by_name(data.name)
            if existing:
                raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"年级 '{data.name}' 已存在")
        
        updated = await self.grade_repo.update(
            grade_id,
            name=data.name,
            description=data.description,
            sort_order=data.sort_order
        )
        await self.db.commit()
        return GradeResponseSchema.model_validate(updated)
    
    async def delete_grade(self, grade_id: int) -> bool:
        """删除年级"""
        grade = await self.grade_repo.get_by_id(grade_id)
        if not grade:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="年级不存在")
        
        ok = await self.grade_repo.delete(grade_id)
        await self.db.commit()
        return ok
    
    # ==================== 学科管理 ====================
    
    async def list_subjects(
        self,
        page: int = 1,
        page_size: int = 100,
        grade_id: Optional[int] = None,
        keyword: Optional[str] = None,
        with_grade: bool = False,
        with_knowledge_points: bool = False,
    ) -> Tuple[Union[List[SubjectResponseSchema], List[SubjectWithGradeSchema], List[SubjectWithKnowledgePointsSchema]], int]:
        """获取学科列表"""
        subjects, total = await self.subject_repo.list(
            page=page,
            page_size=page_size,
            grade_id=grade_id,
            keyword=keyword,
            load_grade=with_grade,
            load_knowledge_points=with_knowledge_points,
        )
        
        if with_grade:
            return [SubjectWithGradeSchema.model_validate(s) for s in subjects], total
        if with_knowledge_points:
            return [SubjectWithKnowledgePointsSchema.model_validate(s) for s in subjects], total
        return [SubjectResponseSchema.model_validate(s) for s in subjects], total
    
    async def list_subjects_by_grade(
        self,
        grade_id: int,
        page: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
        with_knowledge_points: bool = False,
    ) -> Tuple[Union[List[SubjectResponseSchema], List[SubjectWithKnowledgePointsSchema]], int]:
        """获取指定年级的学科列表"""
        grade = await self.grade_repo.get_by_id(grade_id)
        if not grade:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="年级不存在")
        
        subjects, total = await self.subject_repo.list_by_grade(
            grade_id=grade_id,
            page=page,
            page_size=page_size,
            keyword=keyword,
            load_knowledge_points=with_knowledge_points,
        )
        
        if with_knowledge_points:
            return [SubjectWithKnowledgePointsSchema.model_validate(s) for s in subjects], total
        return [SubjectResponseSchema.model_validate(s) for s in subjects], total
    
    async def get_subject(
        self,
        subject_id: int,
        with_grade: bool = False,
        with_knowledge_points: bool = False,
    ) -> Union[SubjectResponseSchema, SubjectWithGradeSchema, SubjectWithKnowledgePointsSchema]:
        """获取学科详情"""
        subject = await self.subject_repo.get_by_id(
            subject_id,
            load_grade=with_grade,
            load_knowledge_points=with_knowledge_points,
        )
        if not subject:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="学科不存在")
        
        if with_grade:
            return SubjectWithGradeSchema.model_validate(subject)
        if with_knowledge_points:
            return SubjectWithKnowledgePointsSchema.model_validate(subject)
        return SubjectResponseSchema.model_validate(subject)
    
    async def create_subject(self, data: SubjectCreateSchema) -> SubjectResponseSchema:
        """创建学科"""
        grade = await self.grade_repo.get_by_id(data.grade_id)
        if not grade:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="年级不存在")
        
        existing = await self.subject_repo.get_by_name_and_grade(data.name, data.grade_id)
        if existing:
            raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"年级 '{grade.name}' 下已存在学科 '{data.name}'")
        
        subject = await self.subject_repo.create(
            name=data.name,
            grade_id=data.grade_id,
            description=data.description,
            sort_order=data.sort_order,
        )
        await self.db.commit()
        return SubjectResponseSchema.model_validate(subject)
    
    async def update_subject(self, subject_id: int, data: SubjectUpdateSchema) -> SubjectResponseSchema:
        """更新学科"""
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="学科不存在")
        
        target_grade_id = data.grade_id if data.grade_id is not None else subject.grade_id
        target_name = data.name if data.name is not None else subject.name
        
        if data.grade_id is not None and data.grade_id != subject.grade_id:
            grade = await self.grade_repo.get_by_id(data.grade_id)
            if not grade:
                raise NotFoundException(code=ErrorCode.NOT_FOUND, message="目标年级不存在")
        
        if (data.name is not None and data.name != subject.name) or (data.grade_id is not None and data.grade_id != subject.grade_id):
            existing = await self.subject_repo.get_by_name_and_grade(target_name, target_grade_id)
            if existing and existing.id != subject_id:
                grade = await self.grade_repo.get_by_id(target_grade_id)
                grade_name = grade.name if grade else str(target_grade_id)
                raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"年级 '{grade_name}' 下已存在学科 '{target_name}'")
        
        updated = await self.subject_repo.update(
            subject_id,
            name=data.name,
            description=data.description,
            grade_id=data.grade_id,
            sort_order=data.sort_order,
        )
        await self.db.commit()
        return SubjectResponseSchema.model_validate(updated)
    
    async def delete_subject(self, subject_id: int) -> bool:
        """删除学科"""
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="学科不存在")
        
        ok = await self.subject_repo.delete(subject_id)
        await self.db.commit()
        return ok
    
    # ==================== 知识点管理 ====================
    
    async def list_knowledge_points(
        self,
        page: int = 1,
        page_size: int = 100,
        grade_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        keyword: Optional[str] = None,
        with_subject: bool = False,
        with_grade: bool = False
    ) -> Tuple[
        Union[
            List[KnowledgePointResponseSchema],
            List[KnowledgePointWithSubjectSchema],
            List[KnowledgePointWithSubjectGradeSchema],
        ],
        int,
    ]:
        """获取知识点列表"""
        load_subject = with_subject or with_grade
        kps, total = await self.kp_repo.list(
            page=page,
            page_size=page_size,
            grade_id=grade_id,
            subject_id=subject_id,
            keyword=keyword,
            load_subject=load_subject,
            load_grade=with_grade,
        )
        
        if with_grade:
            return [KnowledgePointWithSubjectGradeSchema.model_validate(kp) for kp in kps], total
        if with_subject:
            return [KnowledgePointWithSubjectSchema.model_validate(kp) for kp in kps], total
        return [KnowledgePointResponseSchema.model_validate(kp) for kp in kps], total
    

    async def list_knowledge_points_by_subject(
        self,
        subject_id: int,
        page: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
    ) -> Tuple[List[KnowledgePointResponseSchema], int]:
        """获取指定学科的知识点列表"""
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="学科不存在")
        
        kps, total = await self.kp_repo.list_by_subject(
            subject_id=subject_id,
            page=page,
            page_size=page_size,
            keyword=keyword,
        )
        return [KnowledgePointResponseSchema.model_validate(kp) for kp in kps], total
    
    async def get_knowledge_point(
        self,
        kp_id: int,
        with_subject: bool = False,
        with_grade: bool = False,
    ) -> Union[KnowledgePointResponseSchema, KnowledgePointWithSubjectSchema, KnowledgePointWithSubjectGradeSchema]:
        """获取知识点详情"""
        kp = await self.kp_repo.get_by_id(
            kp_id,
            load_subject=with_subject or with_grade,
            load_grade=with_grade,
        )
        if not kp:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="知识点不存在")
        
        if with_grade:
            return KnowledgePointWithSubjectGradeSchema.model_validate(kp)
        if with_subject:
            return KnowledgePointWithSubjectSchema.model_validate(kp)
        return KnowledgePointResponseSchema.model_validate(kp)
    
    async def create_knowledge_point(self, data: KnowledgePointCreateSchema) -> KnowledgePointResponseSchema:
        """创建知识点"""
        subject = await self.subject_repo.get_by_id(data.subject_id)
        if not subject:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="学科不存在")
        
        existing = await self.kp_repo.get_by_name_and_subject(data.name, data.subject_id)
        if existing:
            raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"学科 '{subject.name}' 下已存在知识点 '{data.name}'")
        
        kp = await self.kp_repo.create(
            name=data.name,
            subject_id=data.subject_id,
            description=data.description,
            sort_order=data.sort_order
        )
        await self.db.commit()
        return KnowledgePointResponseSchema.model_validate(kp)
    
    async def update_knowledge_point(self, kp_id: int, data: KnowledgePointUpdateSchema) -> KnowledgePointResponseSchema:
        """更新知识点"""
        kp = await self.kp_repo.get_by_id(kp_id)
        if not kp:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="知识点不存在")
        
        if data.subject_id is not None and data.subject_id != kp.subject_id:
            subject = await self.subject_repo.get_by_id(data.subject_id)
            if not subject:
                raise NotFoundException(code=ErrorCode.NOT_FOUND, message="目标学科不存在")
        
        check_subject_id = data.subject_id if data.subject_id is not None else kp.subject_id
        check_name = data.name if data.name is not None else kp.name
        
        if (data.name is not None and data.name != kp.name) or (data.subject_id is not None and data.subject_id != kp.subject_id):
            existing = await self.kp_repo.get_by_name_and_subject(check_name, check_subject_id)
            if existing and existing.id != kp_id:
                subject = await self.subject_repo.get_by_id(check_subject_id)
                subject_name = subject.name if subject else str(check_subject_id)
                raise AppException(code=ErrorCode.DB_DUPLICATE, message=f"学科 '{subject_name}' 下已存在知识点 '{check_name}'")
        
        updated = await self.kp_repo.update(
            kp_id,
            name=data.name,
            description=data.description,
            subject_id=data.subject_id,
            sort_order=data.sort_order
        )
        await self.db.commit()
        return KnowledgePointResponseSchema.model_validate(updated)
    
    async def delete_knowledge_point(self, kp_id: int) -> bool:
        """删除知识点"""
        kp = await self.kp_repo.get_by_id(kp_id)
        if not kp:
            raise NotFoundException(code=ErrorCode.NOT_FOUND, message="知识点不存在")
        
        ok = await self.kp_repo.delete(kp_id)
        await self.db.commit()
        return ok
