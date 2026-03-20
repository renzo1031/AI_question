"""
AI搜题入库服务
编排「AI 搜题 → 题库入库」完整流程
"""
from typing import Optional, Tuple

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode
from app.common.question_utils import calculate_content_hash, normalize_question_content
from app.core.ai.ai_cache import ai_cache
from app.core.ai.ai_solver import solve_question
from app.core.redis import redis_client
from app.schemas.question import QuestionCreateSchema, QuestionOptionCreateSchema, QuestionResponseSchema
from app.services.question_service import QuestionService
from app.repositories.grade_knowledge_repo import GradeRepository, SubjectRepository, KnowledgePointRepository


class AIQuestionService:
    """
    AI搜题入库服务类
    
    职责：
    1. 接收OCR题干文本
    2. 标准化题干并计算content_hash
    3. 查询Redis缓存或调用AI解题
    4. 调用QuestionService进行数据库去重和入库
    5. 返回题目ID和完整数据
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.question_service = QuestionService(db)
        self.grade_repo = GradeRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.knowledge_point_repo = KnowledgePointRepository(db)
    
    async def solve_and_save_question(
        self,
        ocr_text: str,
        context: Optional[str] = None,
        source: Optional[str] = None,
        tag_ids: Optional[list[int]] = None,
        provider_name: Optional[str] = None
    ) -> QuestionResponseSchema:
        """
        完整的AI搜题入库流程
        
        流程：
        1. 接收OCR题干文本
        2. 对题干进行标准化
        3. 计算content_hash
        4. 查询Redis缓存（命中则使用，未命中则调用AI并缓存）
        5. 调用QuestionService进行数据库去重和入库
        6. 返回question_id + 题目数据
        
        Args:
            ocr_text: OCR识别的题干文本
            context: 上下文信息（可选，传递给AI）
            source: 题目来源（可选）
            tag_ids: 标签ID列表（可选）
            provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
            
        Returns:
            QuestionResponseSchema: 包含question_id和完整题目数据
            
        Raises:
            AppException: 当流程中任何步骤失败时
        """
        content_hash = None  # 初始化变量，用于异常处理
        try:
            # 1. 参数校验
            if not ocr_text or not ocr_text.strip():
                raise AppException(
                    code=ErrorCode.PARAM_ERROR,
                    message="OCR题干文本不能为空"
                )
            
            logger.info(f"开始处理AI搜题入库流程，题干长度: {len(ocr_text)}")
            
            # 2. 题干标准化（使用公共工具函数）
            normalized_content = normalize_question_content(ocr_text)
            logger.debug(f"题干标准化完成，标准化后长度: {len(normalized_content)}")
            
            # 3. 计算content_hash（使用公共工具函数）
            content_hash = calculate_content_hash(normalized_content)
            logger.debug(f"计算content_hash完成: {content_hash[:16]}...")
            
            # 4. 先检查数据库是否已存在该题目（避免不必要的缓存查询）
            existing_question = await self.question_service.question_repo.get_by_content_hash(
                content_hash, load_options=True, load_tags=True
            )
            if existing_question:
                logger.info(f"题目已存在于数据库，直接返回，question_id: {existing_question.id}, content_hash: {content_hash[:16]}...")
                return QuestionResponseSchema.model_validate(existing_question)
            
            # 5. 查询Redis缓存（使用分布式锁防止并发调用）
            # 如果缓存命中，说明之前调用过AI，应该已经入库了，直接查询数据库返回
            # 如果缓存未命中，需要调用AI并入库
            ai_result, cache_hit = await self._get_ai_result_with_cache_status(
                content_hash, normalized_content, context, provider_name
            )
            
            if cache_hit:
                # 缓存命中，说明之前调用过AI，理论上应该已经入库
                # 再次查询数据库（可能是在其他请求中入库的）
                existing_question = await self.question_service.question_repo.get_by_content_hash(
                    content_hash, load_options=True, load_tags=True
                )
                if existing_question:
                    logger.info(f"缓存命中，题目已存在于数据库，直接返回，question_id: {existing_question.id}, content_hash: {content_hash[:16]}...")
                    return QuestionResponseSchema.model_validate(existing_question)
                # 如果数据库中没有，说明缓存是旧的，需要入库
                logger.warning(f"缓存命中但数据库不存在，可能是旧缓存，将重新入库，content_hash: {content_hash[:16]}...")
            
            # 6. 缓存未命中或数据库不存在，需要调用AI并入库
            logger.info(f"获取AI解题结果成功，题目类型: {ai_result.get('question_type')}, 科目: {ai_result.get('subject')}")
            
            # 7. 构建QuestionCreateSchema
            # 先根据AI返回的年级、章节、知识点创建或获取标签ID
            question_data = await self._build_question_create_schema(
                content=normalized_content,
                ai_result=ai_result,
                source=source,
                tag_ids=tag_ids
            )
            
            # 8. 调用QuestionService进行数据库去重和入库
            # QuestionService内部会：
            # - 再次标准化和计算hash（使用公共工具函数，确保一致性）
            # - 检查数据库唯一约束（content_hash）
            # - 如果已存在则直接返回已存在的题目（不抛出异常）
            # - 如果不存在则创建新题目
            question = await self.question_service.create_question(question_data)
            logger.info(f"题目入库成功，question_id: {question.id}, content_hash: {content_hash[:16]}...")
            return question
            
        except AppException:
            # 重新抛出业务异常
            raise
        except Exception as e:
            # 捕获其他异常，转换为业务异常并记录
            logger.error(
                f"AI搜题入库流程异常: content_hash={content_hash[:16] if content_hash else 'N/A'}..., "
                f"error={str(e)}",
                exc_info=True
            )
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"AI搜题入库失败: {str(e)}",
                data={
                    "content_hash": content_hash[:16] if content_hash else None,
                    "original_error": str(e)
                }
            ) from e  # 保留异常链
    
    async def _get_ai_result_with_cache_status(
        self,
        content_hash: str,
        normalized_content: str,
        context: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> tuple[dict, bool]:
        """
        获取AI解题结果（优先从缓存获取，使用分布式锁防止并发调用）
        
        Args:
            content_hash: 题目内容哈希值
            normalized_content: 标准化后的题目内容
            context: 上下文信息（可选）
            provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
            
        Returns:
            (AI解题结果字典, 是否缓存命中)
        """
        try:
            # 1. 先尝试从Redis缓存获取（包含 provider_name 在缓存键中）
            cached_result = await ai_cache.get(content_hash, provider_name=provider_name)
            if cached_result:
                logger.info(f"Redis缓存命中，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                return cached_result, True
            
            # 2. 缓存未命中，使用分布式锁防止并发调用AI
            lock_key = f"ai_solve:{content_hash}"
            lock_identifier = await redis_client.acquire_lock(lock_key, timeout=120, blocking_timeout=10.0)
            
            if not lock_identifier:
                # 获取锁失败，等待一段时间后重试从缓存获取
                import asyncio
                await asyncio.sleep(0.5)
                cached_result = await ai_cache.get(content_hash, provider_name=provider_name)
                if cached_result:
                    logger.info(f"等待后Redis缓存命中，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                    return cached_result, True
                # 如果仍然没有缓存，抛出异常
                raise AppException(
                    code=ErrorCode.AI_SERVICE_ERROR,
                    message="获取AI解题锁失败，请稍后重试"
                )
            
            try:
                # 3. 双重检查：再次尝试从缓存获取（可能其他进程已经写入）
                cached_result = await ai_cache.get(content_hash, provider_name=provider_name)
                if cached_result:
                    logger.info(f"双重检查Redis缓存命中，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                    return cached_result, True
                
                logger.info(f"Redis缓存未命中，开始调用AI解题，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                
                # 4. 调用AI解题（传递 provider_name）
                ai_result = await solve_question(normalized_content, context, provider_name=provider_name)
                
                # 5. 将AI结果写入缓存（包含 provider_name 在缓存键中）
                cache_success = await ai_cache.set(content_hash, ai_result, provider_name=provider_name)
                if cache_success:
                    logger.info(f"AI解题结果已写入Redis缓存，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                else:
                    logger.warning(f"AI解题结果写入Redis缓存失败，提供商: {provider_name or '默认'}，content_hash: {content_hash[:16]}...")
                
                return ai_result, False  # 返回缓存未命中
            finally:
                # 6. 释放锁
                await redis_client.release_lock(lock_key, lock_identifier)
            
        except AppException:
            # 重新抛出业务异常
            raise
        except Exception as e:
            logger.error(
                f"获取AI解题结果异常: content_hash={content_hash[:16]}..., error={str(e)}",
                exc_info=True
            )
            raise AppException(
                code=ErrorCode.AI_SERVICE_ERROR,
                message=f"获取AI解题结果失败: {str(e)}",
                data={"content_hash": content_hash[:16], "original_error": str(e)}
            ) from e  # 保留异常链
    
    async def _get_ai_result(
        self,
        content_hash: str,
        normalized_content: str,
        context: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> dict:
        """
        获取AI解题结果（兼容旧接口，返回结果和缓存状态）
        
        Args:
            content_hash: 题目内容哈希值
            normalized_content: 标准化后的题目内容
            context: 上下文信息（可选）
            provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
            
        Returns:
            AI解题结果字典
        """
        result, _ = await self._get_ai_result_with_cache_status(
            content_hash, normalized_content, context, provider_name
        )
        return result
    
    async def _build_question_create_schema(
        self,
        content: str,
        ai_result: dict,
        source: Optional[str] = None,
        tag_ids: Optional[list[int]] = None
    ) -> QuestionCreateSchema:
        """
        构建QuestionCreateSchema
        
        将AI解题结果转换为题目创建Schema，并自动创建或获取标签
        
        Args:
            content: 标准化后的题目内容
            ai_result: AI解题结果字典
            source: 题目来源（可选）
            tag_ids: 标签ID列表（可选，如果提供则优先使用）
            
        Returns:
            QuestionCreateSchema对象
        """
        # 提取AI结果中的选项
        options = None
        if ai_result.get("options"):
            options = [
                QuestionOptionCreateSchema(
                    option_key=opt.get("option_key", ""),
                    option_text=opt.get("option_text", "")
                )
                for opt in ai_result["options"]
            ]
        
        # 根据AI返回的年级、学科、知识点名称，查找或创建ID
        grade_id, subject_id, knowledge_point_id = await self._resolve_grade_subject_knowledge(
            ai_result.get("grade"),
            ai_result.get("subject"),
            ai_result.get("knowledge_point")
        )
        
        return QuestionCreateSchema(
            content=content,
            question_type=ai_result.get("question_type", "未知类型"),
            subject=ai_result.get("subject", "综合"),
            difficulty=ai_result.get("difficulty", 3),
            source=source or "AI识别",
            grade=ai_result.get("grade"),
            knowledge_point=ai_result.get("knowledge_point"),
            ai_answer=ai_result.get("answer", ""),
            ai_analysis=ai_result.get("analysis", ""),
            options=options,
            tag_ids=tag_ids or [],
            grade_id=grade_id,
            subject_id=subject_id,
            knowledge_point_id=knowledge_point_id
        )
    
    async def _resolve_grade_subject_knowledge(
        self,
        grade_name: Optional[str],
        subject_name: Optional[str],
        knowledge_point_name: Optional[str]
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        根据年级、学科、知识点名称查找或创建ID
        
        Args:
            grade_name: 年级名称（如：一年级、七年级、高一）
            subject_name: 学科名称（如：数学、语文）
            knowledge_point_name: 知识点名称（如：10以内加法、一元一次方程）
            
        Returns:
            (grade_id, subject_id, knowledge_point_id)，失败时返回None
        """
        grade_id = None
        subject_id = None
        knowledge_point_id = None
        
        try:
            # 1. 先获取或创建年级
            if grade_name:
                grade = await self.grade_repo.get_by_name(grade_name.strip())
                if grade:
                    grade_id = grade.id
                else:
                    # 创建新年级
                    new_grade = await self.grade_repo.create(name=grade_name.strip())
                    grade_id = new_grade.id
                    logger.info(f"AI解题自动创建年级: {grade_name} -> ID: {grade_id}")
            
            # 2. 如果有年级和学科，获取或创建学科
            if grade_id and subject_name:
                subject = await self.subject_repo.get_by_name_and_grade(subject_name.strip(), grade_id)
                if subject:
                    subject_id = subject.id
                else:
                    # 创建新学科
                    new_subject = await self.subject_repo.create(
                        name=subject_name.strip(),
                        grade_id=grade_id
                    )
                    subject_id = new_subject.id
                    logger.info(f"AI解题自动创建学科: {subject_name} (年级ID: {grade_id}) -> ID: {subject_id}")
            
            # 3. 如果有学科和知识点，获取或创建知识点
            if subject_id and knowledge_point_name:
                kp = await self.knowledge_point_repo.get_by_name_and_subject(
                    knowledge_point_name.strip(), 
                    subject_id
                )
                if kp:
                    knowledge_point_id = kp.id
                else:
                    # 创建新知识点
                    new_kp = await self.knowledge_point_repo.create(
                        name=knowledge_point_name.strip(),
                        subject_id=subject_id
                    )
                    knowledge_point_id = new_kp.id
                    logger.info(f"AI解题自动创建知识点: {knowledge_point_name} (学科ID: {subject_id}) -> ID: {knowledge_point_id}")
            
            return grade_id, subject_id, knowledge_point_id
            
        except Exception as e:
            logger.error(f"解析年级/学科/知识点失败: {str(e)}", exc_info=True)
            return None, None, None
    

