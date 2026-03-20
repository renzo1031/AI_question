"""
搜题服务
整合OCR识别、AI解题和自动入库功能
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode
from app.core.ai.manager import ai_model_manager
from app.core.ai.ocr import ocr_service
from app.services.ai_question_service import AIQuestionService
from loguru import logger


class QuestionService:
    """搜题服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_question_service = AIQuestionService(db)
    
    async def solve_question_from_image(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        ai_provider: Optional[str] = None,
        context: Optional[str] = None,
        auto_save: bool = True,
        source: Optional[str] = None,
        tag_ids: Optional[list[int]] = None
    ) -> dict:
        """
        从图片识别题目并解题（自动入库）
        
        Args:
            image_url: 图片URL
            image_base64: 图片Base64编码（会自动解码为二进制数据）
            image_bytes: 图片二进制数据（与image_url、image_base64三选一）
            ai_provider: AI提供商名称（tongyi/deepseek/kimi）
            context: 上下文信息（可选）
            auto_save: 是否自动入库（默认True）
            source: 题目来源（可选，用于入库）
            tag_ids: 标签ID列表（可选，用于入库）
            
        Returns:
            包含识别结果、解题答案和题目信息的字典
            - 如果 auto_save=True: 包含 question_id 和完整题目信息
            - 如果 auto_save=False: 仅包含解题结果（兼容旧接口）
        """
        try:
            # 1. OCR识别题目
            logger.info("开始OCR识别题目...")
            ocr_result = await ocr_service.recognize_question(
                image_url=image_url,
                image_base64=image_base64,
                image_bytes=image_bytes
            )
            
            question_content = ocr_result.get("content", "")
            if not question_content:
                raise AppException(
                    code=ErrorCode.PARAM_ERROR,
                    message="未能识别出题目内容，请检查图片质量"
                )
            
            logger.info(f"OCR识别成功，题目长度: {len(question_content)}")
            
            # 2. 如果启用自动入库，使用AI搜题入库服务
            if auto_save:
                logger.info("启用自动入库，调用AI搜题入库服务...")
                question = await self.ai_question_service.solve_and_save_question(
                    ocr_text=question_content,
                    context=context,
                    source=source or "图片识别",
                    tag_ids=tag_ids,
                    provider_name=ai_provider  # 传递用户指定的AI提供商
                )
                
                # 返回包含题目ID和完整信息的响应
                return {
                    "question": {
                        "id": question.id,
                        "content": question.content,
                        "question_type": question.question_type,
                        "subject": question.subject,
                        "difficulty": question.difficulty,
                        "figure": ocr_result.get("figure", []),
                        "width": ocr_result.get("width", 0),
                        "height": ocr_result.get("height", 0)
                    },
                    "answer": {
                        "content": question.ai_answer or "",
                        "analysis": question.ai_analysis or "",
                        "options": [{"option_key": opt.option_key, "option_text": opt.option_text} 
                                   for opt in question.options] if question.options else []
                    },
                    "saved": True,
                    "question_id": question.id
                }
            
            # 3. 如果不自动入库，使用原有的AI解题流程（兼容旧接口）
            logger.info(f"不自动入库，使用AI解题，提供商: {ai_provider or '默认'}")
            ai_result = await ai_model_manager.solve_question(
                question=question_content,
                provider_name=ai_provider,
                context=context
            )
            
            logger.info("AI解题完成")
            
            # 4. 组合返回结果（兼容旧格式）
            return {
                "question": {
                    "content": question_content,
                    "figure": ocr_result.get("figure", []),
                    "width": ocr_result.get("width", 0),
                    "height": ocr_result.get("height", 0)
                },
                "answer": {
                    "content": ai_result.get("answer", ""),
                    "provider": ai_result.get("provider", ""),
                    "model": ai_result.get("model", "")
                },
                "saved": False
            }
        except ValueError as e:
            logger.error("参数错误: {}", str(e))
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message=str(e)
            )
        except Exception as e:
            logger.error("搜题服务异常: {}", str(e), exc_info=True)
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"搜题失败: {str(e)}"
            )
    
    async def solve_question_from_text(
        self,
        question_text: str,
        ai_provider: Optional[str] = None,
        context: Optional[str] = None,
        auto_save: bool = True,
        source: Optional[str] = None,
        tag_ids: Optional[list[int]] = None
    ) -> dict:
        """
        直接解题（不需要OCR，自动入库）
        
        Args:
            question_text: 题目文本
            ai_provider: AI提供商名称（tongyi/deepseek/kimi，已废弃，使用统一的AI解题服务）
            context: 上下文信息（可选）
            auto_save: 是否自动入库（默认True）
            source: 题目来源（可选，用于入库）
            tag_ids: 标签ID列表（可选，用于入库）
            
        Returns:
            包含解题答案和题目信息的字典
            - 如果 auto_save=True: 包含 question_id 和完整题目信息
            - 如果 auto_save=False: 仅包含解题结果（兼容旧接口）
        """
        if not question_text or not question_text.strip():
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message="题目内容不能为空"
            )
        
        try:
            # 1. 如果启用自动入库，使用AI搜题入库服务
            if auto_save:
                logger.info("启用自动入库，调用AI搜题入库服务...")
                question = await self.ai_question_service.solve_and_save_question(
                    ocr_text=question_text,
                    context=context,
                    source=source or "文本输入",
                    tag_ids=tag_ids,
                    provider_name=ai_provider  # 传递用户指定的AI提供商
                )
                
                # 返回包含题目ID和完整信息的响应
                return {
                    "question": {
                        "id": question.id,
                        "content": question.content,
                        "question_type": question.question_type,
                        "subject": question.subject,
                        "difficulty": question.difficulty
                    },
                    "answer": {
                        "content": question.ai_answer or "",
                        "analysis": question.ai_analysis or "",
                        "options": [{"option_key": opt.option_key, "option_text": opt.option_text} 
                                   for opt in question.options] if question.options else []
                    },
                    "saved": True,
                    "question_id": question.id
                }
            
            # 2. 如果不自动入库，使用原有的AI解题流程（兼容旧接口）
            logger.info(f"不自动入库，使用AI解题，提供商: {ai_provider or '默认'}")
            ai_result = await ai_model_manager.solve_question(
                question=question_text,
                provider_name=ai_provider,
                context=context
            )
            
            logger.info("AI解题完成")
            
            return {
                "question": {
                    "content": question_text
                },
                "answer": {
                    "content": ai_result.get("answer", ""),
                    "provider": ai_result.get("provider", ""),
                    "model": ai_result.get("model", "")
                },
                "saved": False
            }
        except ValueError as e:
            logger.error("参数错误: {}", str(e))
            raise AppException(
                code=ErrorCode.PARAM_ERROR,
                message=str(e)
            )
        except Exception as e:
            logger.error("解题服务异常: {}", str(e), exc_info=True)
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"解题失败: {str(e)}"
            )
    
    def get_available_ai_providers(self) -> list[str]:
        """获取可用的AI提供商列表"""
        return ai_model_manager.list_available_providers()

