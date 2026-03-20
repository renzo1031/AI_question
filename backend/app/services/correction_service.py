"""
题目纠错业务服务层
"""
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode, NotFoundException
from app.repositories.correction_repo import CorrectionRepository
from app.repositories.question_repo import QuestionRepository
from app.schemas.correction import (
    QuestionCorrectionCreateSchema,
    QuestionCorrectionListSchema,
    QuestionCorrectionQuerySchema,
    QuestionCorrectionResponseSchema,
    QuestionCorrectionUpdateSchema,
)


class CorrectionService:
    """纠错服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.correction_repo = CorrectionRepository(db)
        self.question_repo = QuestionRepository(db)
    
    async def submit_correction(
        self,
        data: QuestionCorrectionCreateSchema,
        user_id: Optional[str] = None
    ) -> QuestionCorrectionResponseSchema:
        """
        用户提交纠错
        
        Args:
            data: 纠错数据
            user_id: 提交用户ID（可选，允许匿名提交）
            
        Returns:
            纠错记录
        """
        try:
            # 验证题目是否存在
            question = await self.question_repo.get_by_id(data.question_id)
            if not question:
                raise NotFoundException(
                    code=ErrorCode.NOT_FOUND,
                    message="题目不存在"
                )
            
            # 创建纠错记录
            correction = await self.correction_repo.create(
                question_id=data.question_id,
                user_id=user_id,
                reason=data.reason
            )
            
            logger.info(f"用户提交纠错成功: correction_id={correction.id}, question_id={data.question_id}, user_id={user_id}")
            return QuestionCorrectionResponseSchema.model_validate(correction)
            
        except AppException:
            raise
        except Exception as e:
            logger.error(f"提交纠错失败: {str(e)}", exc_info=True)
            raise AppException(
                code=ErrorCode.DB_ERROR,
                message=f"提交纠错失败: {str(e)}"
            )
    
    async def list_corrections(
        self,
        query: QuestionCorrectionQuerySchema,
        user_id: Optional[str] = None,
        admin_mode: bool = False
    ) -> QuestionCorrectionListSchema:
        """
        获取纠错列表
        
        Args:
            query: 查询参数
            user_id: 用户ID（非管理员模式时只能查看自己的）
            admin_mode: 是否管理员模式
            
        Returns:
            纠错列表
        """
        try:
            # 非管理员模式只能查看自己的纠错
            filter_user_id = None if admin_mode else user_id
            
            corrections, total = await self.correction_repo.list(
                page=query.page,
                page_size=query.page_size,
                status=query.status,
                question_id=query.question_id,
                user_id=filter_user_id
            )
            
            # 计算总页数
            total_pages = (total + query.page_size - 1) // query.page_size if total > 0 else 0
            
            return QuestionCorrectionListSchema(
                items=[QuestionCorrectionResponseSchema.model_validate(c) for c in corrections],
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"获取纠错列表失败: {str(e)}", exc_info=True)
            raise AppException(
                code=ErrorCode.DB_ERROR,
                message=f"获取纠错列表失败: {str(e)}"
            )
    
    async def handle_correction(
        self,
        correction_id: int,
        data: QuestionCorrectionUpdateSchema,
        admin_id: str
    ) -> QuestionCorrectionResponseSchema:
        """
        管理员处理纠错
        
        Args:
            correction_id: 纠错记录ID
            data: 更新数据
            admin_id: 管理员ID
            
        Returns:
            更新后的纠错记录
        """
        try:
            # 检查纠错记录是否存在
            correction = await self.correction_repo.get_by_id(correction_id)
            if not correction:
                raise NotFoundException(
                    code=ErrorCode.NOT_FOUND,
                    message="纠错记录不存在"
                )
            
            # 更新状态
            updated_correction = await self.correction_repo.update_status(
                correction_id=correction_id,
                status=data.status,
                admin_note=data.admin_note,
                handled_by=admin_id
            )
            
            logger.info(
                f"管理员处理纠错: correction_id={correction_id}, "
                f"status={data.status}, admin_id={admin_id}"
            )
            return QuestionCorrectionResponseSchema.model_validate(updated_correction)
            
        except AppException:
            raise
        except Exception as e:
            logger.error(f"处理纠错失败: {str(e)}", exc_info=True)
            raise AppException(
                code=ErrorCode.DB_ERROR,
                message=f"处理纠错失败: {str(e)}"
            )
    
    async def get_pending_count(self) -> int:
        """获取待处理纠错数量"""
        try:
            return await self.correction_repo.count_by_status("pending")
        except Exception as e:
            logger.error(f"获取待处理纠错数量失败: {str(e)}", exc_info=True)
            return 0
