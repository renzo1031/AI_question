"""
练习服务
提供练习出题的完整业务流程
"""
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AppException, ErrorCode
from app.common.question_utils import calculate_content_hash, normalize_question_content
from app.core.ai.ai_generate_questions import generate_questions
from app.repositories.practice_repo import PracticeRepository
from app.repositories.question_repo import QuestionRepository
from app.schemas.practice import PracticeGenerateSchema, PracticeQuestionSchema
from app.schemas.question import QuestionCreateSchema, QuestionOptionCreateSchema
from app.services.question_service import QuestionService


class PracticeService:
    """练习服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.practice_repo = PracticeRepository(db)
        self.question_repo = QuestionRepository(db)
        self.question_service = QuestionService(db)
    
    async def generate_practice_questions(
        self,
        user_id: int,
        generate_schema: PracticeGenerateSchema
    ) -> list[PracticeQuestionSchema]:
        """
        生成练习题
        
        完整流程：
        1. 组合 tags（年级/章节/知识点）
        2. 优先从题库查询
        3. 如果题库数量 < count：
           - 调用 AI 出题
           - 对 AI 题目进行标准化、去重、入库
        4. 再次从题库中查询，补齐题目数量
        5. 返回 PracticeQuestionSchema 列表
        
        Args:
            generate_schema: 生成练习题请求Schema
            
        Returns:
            练习题列表（PracticeQuestionSchema）
        """
        try:
            # 1. 组合 tags（年级/章节/知识点）
            tag_names = []
            if generate_schema.grade:
                tag_names.append(generate_schema.grade)
            if generate_schema.chapter:
                tag_names.append(generate_schema.chapter)
            if generate_schema.knowledge_point:
                tag_names.append(generate_schema.knowledge_point)
            
            logger.info(
                f"开始生成练习题，学科: {generate_schema.subject}, "
                f"标签: {tag_names}, 数量: {generate_schema.count}"
            )
            
            # 2. 优先从题库查询
            questions = await self.practice_repo.list_questions_by_filters(
                subject=generate_schema.subject,
                tags_all=tag_names,
                question_type=generate_schema.question_type,
                difficulty=generate_schema.difficulty,
                limit=generate_schema.count
            )
            
            logger.info(f"从题库查询到 {len(questions)} 道题目")
            
            # 3. 如果题库数量 < count，调用 AI 出题并入库
            if len(questions) < generate_schema.count:
                needed_count = generate_schema.count - len(questions)
                logger.info(f"题库数量不足，需要 AI 生成 {needed_count} 道题目")
                
                # 调用 AI 出题（生成数量 + buffer，确保有足够的题目）
                buffer = max(2, needed_count // 2)  # buffer 至少为2，或为需要数量的50%
                ai_questions = await generate_questions(
                    subject=generate_schema.subject,
                    grade=generate_schema.grade,
                    chapter=generate_schema.chapter,
                    knowledge_point=generate_schema.knowledge_point,
                    question_type=generate_schema.question_type,
                    difficulty=generate_schema.difficulty,
                    count=needed_count + buffer
                )
                
                logger.info(f"AI 生成 {len(ai_questions)} 道题目")
                
                # 对 AI 题目进行标准化、去重、入库
                saved_count = 0
                failed_count = 0
                failed_questions = []
                
                for ai_question in ai_questions:
                    try:
                        # 标准化 content
                        normalized_content = normalize_question_content(ai_question["content"])
                        
                        # 计算 content_hash
                        content_hash = calculate_content_hash(normalized_content)
                        
                        # 检查是否已存在（去重）
                        existing_question = await self.question_repo.get_by_content_hash(
                            content_hash, load_options=False, load_tags=False
                        )
                        if existing_question:
                            logger.debug(f"题目已存在（content_hash: {content_hash[:16]}...），跳过")
                            continue
                        
                        # 统一标签来源：优先使用用户输入的标签，确保查询和入库使用相同的标签
                        # 这样入库的题目可以被后续查询匹配到
                        question_tag_names = []
                        if generate_schema.grade:
                            question_tag_names.append(generate_schema.grade)
                        if generate_schema.chapter:
                            question_tag_names.append(generate_schema.chapter)
                        if generate_schema.knowledge_point:
                            question_tag_names.append(generate_schema.knowledge_point)
                        
                        # 如果AI返回的标签有额外的且不在用户输入中，可以追加（但不强制）
                        ai_tags = ai_question.get("tags", [])
                        for tag in ai_tags:
                            if tag and tag.strip() and tag not in question_tag_names:
                                question_tag_names.append(tag.strip())
                        
                        # 如果仍然没有标签，使用默认值（而不是"未分类"）
                        if not question_tag_names:
                            question_tag_names = ["未知年级", "未知章节", "未知知识点"]
                        elif len(question_tag_names) == 1:
                            question_tag_names.extend(["未知章节", "未知知识点"])
                        elif len(question_tag_names) == 2:
                            question_tag_names.append("未知知识点")
                        
                        tag_ids = await self.question_repo.get_or_create_tags_by_names(question_tag_names)
                        
                        # 构建选项（从 AI 返回的 options 字段中获取）
                        ai_options = ai_question.get("options", [])
                        options = []
                        if ai_options and isinstance(ai_options, list):
                            for opt in ai_options:
                                if isinstance(opt, dict) and "option_key" in opt and "option_text" in opt:
                                    options.append(QuestionOptionCreateSchema(
                                        option_key=opt["option_key"],
                                        option_text=opt["option_text"],
                                        is_correct=(opt["option_key"] == ai_question.get("answer"))
                                    ))
                        
                        # 构建 QuestionCreateSchema
                        question_data = QuestionCreateSchema(
                            content=normalized_content,
                            question_type=ai_question.get("question_type", "未知类型"),
                            subject=ai_question.get("subject") or generate_schema.subject,
                            difficulty=ai_question.get("difficulty", 3),
                            source="AI生成",
                            grade=ai_question.get("grade") or generate_schema.grade,
                            knowledge_point=ai_question.get("knowledge_point") or generate_schema.knowledge_point,
                            ai_answer=ai_question.get("answer", ""),
                            ai_analysis=ai_question.get("analysis", ""),
                            options=options or [],
                            tag_ids=tag_ids
                        )
                        
                        # 调用 QuestionService 入库（会自动去重并返回题目）
                        # create_question 内部会处理去重，如果已存在则返回已存在的题目
                        # 添加重试机制（对于非重复插入错误）
                        max_retries = 3
                        last_error = None
                        for retry in range(max_retries):
                            try:
                                await self.question_service.create_question(question_data)
                                saved_count += 1
                                logger.debug(f"AI题目入库成功，content_hash: {content_hash[:16]}...")
                                break
                            except Exception as e:
                                last_error = e
                                # 如果是重复插入错误，不需要重试
                                if isinstance(e, AppException) and e.code == ErrorCode.DB_DUPLICATE:
                                    logger.debug(f"题目已存在（content_hash: {content_hash[:16]}...），跳过")
                                    break
                                
                                # 如果是最后一次重试，抛出异常
                                if retry == max_retries - 1:
                                    raise
                                
                                # 指数退避重试
                                import asyncio
                                wait_time = 0.5 * (retry + 1)
                                logger.warning(
                                    f"AI题目入库失败，重试 {retry + 1}/{max_retries}，"
                                    f"等待 {wait_time} 秒后重试，content_hash: {content_hash[:16]}...，错误: {str(e)}"
                                )
                                await asyncio.sleep(wait_time)
                        
                    except Exception as e:
                        # 单个题目入库失败，记录详细信息
                        failed_count += 1
                        failed_info = {
                            "content_preview": ai_question.get("content", "")[:100],
                            "error": str(e),
                            "content_hash": content_hash[:16] + "..." if 'content_hash' in locals() else "N/A"
                        }
                        failed_questions.append(failed_info)
                        logger.warning(
                            f"AI题目入库失败 ({failed_count}/{len(ai_questions)}): {str(e)}, "
                            f"content: {failed_info['content_preview']}...",
                            exc_info=True
                        )
                        continue
                
                # 记录入库结果统计
                logger.info(
                    f"AI题目入库完成，成功: {saved_count}/{len(ai_questions)}, "
                    f"失败: {failed_count}/{len(ai_questions)}"
                )
                
                # 如果失败率过高（超过50%），记录错误日志
                if failed_count > 0:
                    failure_rate = failed_count / len(ai_questions) * 100
                    if failure_rate > 50:
                        logger.error(
                            f"AI题目入库失败率过高: {failure_rate:.1f}% ({failed_count}/{len(ai_questions)}), "
                            f"失败详情: {failed_questions}"
                        )
                    else:
                        logger.warning(
                            f"AI题目入库部分失败: {failure_rate:.1f}% ({failed_count}/{len(ai_questions)}), "
                            f"失败详情: {failed_questions}"
                        )
            
            # 4. 再次从题库中查询，补齐题目数量
            # 排除已获取的题目ID，避免重复
            existing_question_ids = {q.id for q in questions}
            remaining_count = generate_schema.count - len(questions)
            
            if remaining_count > 0:
                # 重新查询（可能会包含新入库的题目）
                additional_questions = await self.practice_repo.list_questions_by_filters(
                    subject=generate_schema.subject,
                    tags_all=tag_names,
                    question_type=generate_schema.question_type,
                    difficulty=generate_schema.difficulty,
                    limit=generate_schema.count * 2  # 多查询一些，避免重复
                )
                
                # 过滤掉已存在的题目
                for q in additional_questions:
                    if q.id not in existing_question_ids and len(questions) < generate_schema.count:
                        questions.append(q)
                        existing_question_ids.add(q.id)
            
            # 5. 转换为 PracticeQuestionSchema 并返回
            result = []
            for question in questions[:generate_schema.count]:
                # 转换 sub_knowledge_points 为字符串列表
                question_tags = [skp.name for skp in question.sub_knowledge_points] if question.sub_knowledge_points else []
                
                # 构建 PracticeQuestionSchema
                practice_question = PracticeQuestionSchema(
                    id=question.id,
                    content=question.content,
                    question_type=question.question_type or "",
                    difficulty=question.difficulty or 1,
                    options=[],  # 如果需要可以加载 options
                    tags=question_tags
                )
                result.append(practice_question)
            
            logger.info(f"练习出题完成，返回 {len(result)} 道题目")
            return result
            
        except AppException:
            # 重新抛出业务异常
            raise
        except Exception as e:
            # 捕获其他异常，转换为业务异常
            logger.error(f"生成练习题异常: {str(e)}", exc_info=True)
            raise AppException(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"生成练习题失败: {str(e)}"
            )
    
    def _compare_answer(self, user_answer: str, correct_answer: str, question_type: Optional[str] = None) -> bool:
        """
        比较用户答案和正确答案（使用策略模式）
        
        Args:
            user_answer: 用户答案
            correct_answer: 正确答案
            question_type: 题目类型（可选）
            
        Returns:
            是否匹配
        """
        from app.core.answer_comparator import AnswerComparatorFactory
        
        # 使用工厂获取对应的比较器
        comparator = AnswerComparatorFactory.get_comparator(question_type)
        return comparator.compare(user_answer, correct_answer)
    
    async def check_and_record_answer(
        self,
        user_id: int,
        question_id: int,
        user_answer: str
    ) -> dict:
        """
        校验用户答案
        
        Args:
            user_id: 用户ID（用于记录答题结果）
            question_id: 题目ID
            user_answer: 用户答案
            record_result: 是否记录答题结果（默认True，用于错题本功能）
            
        Returns:
            包含校验结果的字典：
            - is_correct: 是否正确
            - correct_answer: 正确答案
            - analysis: 解析
        """
        # 获取题目信息（含 ai_answer/ai_analysis）
        question = await self.practice_repo.get_question_by_id(question_id)
        if not question:
            from app.common.exceptions import NotFoundException
            raise NotFoundException(
                code=ErrorCode.NOT_FOUND,
                message="题目不存在"
            )
        
        # 获取正确答案
        correct_answer = question.ai_answer or ""
        
        # 判题：使用可扩展的 compare_answer 策略
        is_correct = self._compare_answer(
            user_answer=user_answer,
            correct_answer=correct_answer,
            question_type=question.question_type
        )
        
        # 调用 UserQuestionService.record_answer 写入错题本数据
        from app.services.user_question_service import UserQuestionService
        user_question_service = UserQuestionService(self.db)
        await user_question_service.record_answer(
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct
        )
        
        logger.debug(f"用户 {user_id} 答题记录已保存，题目 {question_id}，结果: {'正确' if is_correct else '错误'}")
        
        # 返回 PracticeCheckResultSchema 格式
        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "analysis": question.ai_analysis or ""
        }
    
    async def generate_practice_from_wrongbook(
        self,
        user_id: int,
        generate_schema: PracticeGenerateSchema
    ) -> list[PracticeQuestionSchema]:
        """
        从错题本生成练习题（错题再练）
        
        出题逻辑：
        1. 优先从 user_question.status=wrong 的题目中抽取
        2. 数量不足时回退到题库查询
        3. 仍不足时调用 AI 补题
        
        Args:
            user_id: 用户ID
            generate_schema: 生成练习题请求Schema
            
        Returns:
            练习题列表（PracticeQuestionSchema）
        """
        from app.services.user_question_service import UserQuestionService
        
        # 组装 tags_all
        tags_all = []
        if generate_schema.grade:
            tags_all.append(generate_schema.grade)
        if generate_schema.chapter:
            tags_all.append(generate_schema.chapter)
        if generate_schema.knowledge_point:
            tags_all.append(generate_schema.knowledge_point)
        
        questions = []
        existing_ids = set()
        
        # 1. 优先从错题本中查询
        user_question_service = UserQuestionService(self.db)
        wrong_questions = await user_question_service.list_wrong_questions_for_practice(
            user_id=user_id,
            subject=generate_schema.subject,
            tags_all=tags_all,
            difficulty=generate_schema.difficulty,
            limit=generate_schema.count,
            offset=0
        )
        
        for q in wrong_questions:
            questions.append(q)
            existing_ids.add(q.id)
        
        logger.info(f"从错题本查询到 {len(questions)} 道题目")
        
        # 2. 如果错题本数量不足，从题库补充
        if len(questions) < generate_schema.count:
            needed_count = generate_schema.count - len(questions)
            
            additional_questions = await self.practice_repo.list_questions_by_filters(
                subject=generate_schema.subject,
                tags_all=tags_all,
                question_type=generate_schema.question_type,
                difficulty=generate_schema.difficulty,
                limit=needed_count * 2  # 多查询一些，避免重复
            )
            
            for q in additional_questions:
                if q.id not in existing_ids and len(questions) < generate_schema.count:
                    questions.append(q)
                    existing_ids.add(q.id)
            
            logger.info(f"从题库补充 {len(questions) - len(wrong_questions)} 道题目")
        
        # 3. 如果仍不足，调用 AI 补题（通过 generate_practice_questions）
        if len(questions) < generate_schema.count:
            remaining_count = generate_schema.count - len(questions)
            original_count = generate_schema.count
            
            # 临时修改 count 为剩余数量
            generate_schema.count = remaining_count
            
            try:
                # 调用 AI 补题（会自动入库）
                ai_questions = await self.generate_practice_questions(user_id, generate_schema)
                
                # 合并结果（需要从数据库加载完整题目对象）
                for ai_q in ai_questions:
                    if ai_q.id not in existing_ids and len(questions) < original_count:
                        question = await self.practice_repo.get_question_by_id(ai_q.id)
                        if question:
                            questions.append(question)
                            existing_ids.add(question.id)
            finally:
                # 恢复原始 count
                generate_schema.count = original_count
            
            logger.info(f"AI补题 {len(questions) - len(existing_ids) + len(wrong_questions)} 道题目")
        
        # 转换为 PracticeQuestionSchema
        result = []
        for question in questions[:generate_schema.count]:
            question_tags = [skp.name for skp in question.sub_knowledge_points] if question.sub_knowledge_points else []
            practice_question = PracticeQuestionSchema(
                id=question.id,
                content=question.content,
                question_type=question.question_type or "",
                difficulty=question.difficulty or 1,
                options=[],  # 如果需要可以加载 options
                tags=question_tags
            )
            result.append(practice_question)
        
        logger.info(f"错题再练完成，返回 {len(result)} 道题目")
        return result

