"""
AI出题模块
负责调用大模型生成练习题，不涉及数据库操作
"""
import json
import re
from typing import Optional

from loguru import logger

from app.common.exceptions import AppException, ErrorCode
from app.core.ai.manager import ai_model_manager
from app.core.ai.prompts import build_generate_questions_prompt


async def call_llm_for_generation(prompt: str, provider_name: Optional[str] = None) -> str:
    """
    调用大模型生成题目，返回原始文本响应
    
    使用 AI 模型管理器获取对应的提供商，并调用其 call_raw 方法
    
    Args:
        prompt: 完整的提示词
        provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
        
    Returns:
        AI返回的文本内容
        
    Raises:
        AppException: 当AI服务调用失败时
    """
    try:
        # 使用 AI 模型管理器获取对应的提供商
        provider = ai_model_manager.get_provider(provider_name)
        
        # 调用提供商的 call_raw 方法
        ai_response = await provider.call_raw(prompt)
        
        if not ai_response or not ai_response.strip():
            raise AppException(
                ErrorCode.AI_SERVICE_ERROR,
                "AI服务返回结果为空"
            )
        
        return ai_response
        
    except ValueError as e:
        # 提供商不可用
        logger.error(f"AI提供商不可用: {str(e)}")
        raise AppException(
            ErrorCode.AI_SERVICE_ERROR,
            f"AI提供商不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"调用AI模型失败: {str(e)}", exc_info=True)
        raise AppException(
            ErrorCode.AI_SERVICE_ERROR,
            f"AI服务调用失败: {str(e)}"
        )


def _extract_json_array_from_text(text: str) -> str:
    """
    从文本中提取JSON数组内容
    
    尝试从AI返回的文本中提取纯JSON数组部分，去除可能的自然语言前缀或后缀
    
    Args:
        text: 原始文本
        
    Returns:
        提取的JSON数组字符串
        
    Raises:
        AppException: 当无法提取有效JSON数组时
    """
    if not text or not text.strip():
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            "AI返回结果为空"
        )
    
    # 去除首尾空白
    text = text.strip()
    
    # 尝试直接解析（如果已经是纯JSON数组）
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return text
    except json.JSONDecodeError:
        pass
    
    # 尝试提取JSON数组（使用正则表达式）
    # 匹配 [...] 格式的JSON数组
    json_array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    matches = re.findall(json_array_pattern, text, re.DOTALL)
    
    if matches:
        # 尝试解析最长的匹配项（通常是完整的JSON数组）
        for match in sorted(matches, key=len, reverse=True):
            try:
                parsed = json.loads(match)
                if isinstance(parsed, list):
                    return match
            except json.JSONDecodeError:
                continue
    
    # 尝试提取代码块中的JSON数组（```json ... ``` 或 ``` ... ```）
    code_block_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
    code_matches = re.findall(code_block_pattern, text, re.DOTALL)
    if code_matches:
        for match in code_matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, list):
                    return match
            except json.JSONDecodeError:
                continue
    
    # 如果都失败了，抛出异常
    raise AppException(
        ErrorCode.AI_JSON_PARSE_ERROR,
        f"无法从AI返回结果中提取有效JSON数组。返回内容: {text[:200]}..."
    )


def _validate_question_item(data: dict, index: int) -> None:
    """
    校验单道题目的JSON数据是否包含所有必需字段
    
    Args:
        data: 解析后的题目字典
        index: 题目在数组中的索引（用于错误提示）
        
    Raises:
        AppException: 当缺少必需字段或字段格式不正确时
    """
    required_fields = {
        "content": str,
        "question_type": str,
        "difficulty": int,
        "answer": str,
        "analysis": str,
        "options": list,
        "tags": list
    }
    
    # 检查必需字段是否存在
    missing_fields = []
    for field, field_type in required_fields.items():
        if field not in data:
            missing_fields.append(field)
        elif not isinstance(data[field], field_type):
            raise AppException(
                ErrorCode.AI_RESPONSE_INVALID,
                f"题目 {index} 的字段 '{field}' 类型错误，期望 {field_type.__name__}，实际 {type(data[field]).__name__}"
            )
    
    if missing_fields:
        raise AppException(
            ErrorCode.AI_RESPONSE_MISSING_FIELD,
            f"题目 {index} 缺少必需字段: {', '.join(missing_fields)}"
        )
    
    # 校验字符串字段不能为空
    string_fields = ["content", "question_type", "answer", "analysis"]
    for field in string_fields:
        if not data[field] or not data[field].strip():
            raise AppException(
                ErrorCode.AI_RESPONSE_INVALID,
                f"题目 {index} 的字段 '{field}' 不能为空"
            )
    
    # 校验 difficulty 范围
    difficulty = data["difficulty"]
    if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"题目 {index} 的字段 'difficulty' 必须是1-5之间的整数，实际值: {difficulty}"
        )
    
    # 校验 tags 格式
    tags = data["tags"]
    if not isinstance(tags, list):
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"题目 {index} 的字段 'tags' 必须是数组，实际类型: {type(tags).__name__}"
        )
    
    if len(tags) < 3:
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"题目 {index} 的字段 'tags' 必须包含至少3个元素（年级、章节、知识点），实际数量: {len(tags)}"
        )
    
    # 校验 tags 中的元素都是字符串
    for i, tag in enumerate(tags):
        if not isinstance(tag, str) or not tag.strip():
            raise AppException(
                ErrorCode.AI_RESPONSE_INVALID,
                f"题目 {index} 的 tags[{i}] 必须是非空字符串"
            )


def _validate_questions_array(data: list) -> None:
    """
    校验题目数组
    
    Args:
        data: 解析后的题目数组
        
    Raises:
        AppException: 当数组格式不正确时
    """
    if not isinstance(data, list):
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"AI返回结果必须是数组，实际类型: {type(data).__name__}"
        )
    
    if len(data) == 0:
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            "AI返回的题目数组为空"
        )
    
    # 校验每道题目
    for i, question in enumerate(data):
        _validate_question_item(question, i)


async def generate_questions(
    subject: str,
    grade: Optional[str] = None,
    chapter: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[int] = None,
    count: int = 10,
    provider_name: Optional[str] = None
) -> list[dict]:
    """
    AI出题主函数
    
    根据条件生成练习题，返回题目列表
    
    Args:
        subject: 学科（必填）
        grade: 年级（可选，如：七年级）
        chapter: 章节（可选，如：第一章）
        knowledge_point: 知识点（可选）
        question_type: 题目类型（可选）
        difficulty: 难度等级（可选，1-5）
        count: 题目数量（默认10）
        provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
        
    Returns:
        题目列表，每个题目包含：
        {
            "content": str,           # 题目内容
            "question_type": str,     # 题目类型
            "difficulty": int,        # 难度（1-5）
            "answer": str,            # 答案
            "analysis": str,          # 解析
            "tags": list[str]         # 标签列表（年级、章节、知识点）
        }
        
    Raises:
        AppException: 当AI服务调用失败、JSON解析失败或数据校验失败时
    """
    if not subject or not subject.strip():
        raise AppException(
            ErrorCode.PARAM_ERROR,
            "学科不能为空"
        )
    
    if count < 1 or count > 100:
        raise AppException(
            ErrorCode.PARAM_ERROR,
            "题目数量必须在1-100之间"
        )
    
    try:
        # 1. 构建Prompt
        prompt = build_generate_questions_prompt(
            subject=subject,
            grade=grade,
            chapter=chapter,
            knowledge_point=knowledge_point,
            question_type=question_type,
            difficulty=difficulty,
            count=count
        )
        logger.debug(f"构建的出题Prompt长度: {len(prompt)}")
        
        # 2. 调用大模型
        logger.info(f"开始调用AI模型出题，学科: {subject}, 数量: {count}, 提供商: {provider_name or '默认'}...")
        ai_response = await call_llm_for_generation(prompt, provider_name=provider_name)
        
        if not ai_response or not ai_response.strip():
            raise AppException(
                ErrorCode.AI_SERVICE_ERROR,
                "AI服务返回结果为空"
            )
        
        logger.debug(f"AI返回结果长度: {len(ai_response)}")
        logger.debug(f"AI返回结果预览: {ai_response[:200]}...")
        
        # 3. 提取JSON数组内容
        json_text = _extract_json_array_from_text(ai_response)
        logger.debug(f"提取的JSON数组长度: {len(json_text)}")
        
        # 4. 解析JSON数组
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}, JSON内容: {json_text[:500]}")
            raise AppException(
                ErrorCode.AI_JSON_PARSE_ERROR,
                f"AI返回的JSON格式无效: {str(e)}"
            )
        
        # 5. 校验数据
        _validate_questions_array(data)
        
        logger.info(f"AI出题成功，生成 {len(data)} 道题目")
        return data
        
    except AppException:
        # 重新抛出业务异常
        raise
    except Exception as e:
        # 捕获其他异常，转换为业务异常
        logger.error(f"AI出题过程发生异常: {str(e)}", exc_info=True)
        raise AppException(
            ErrorCode.AI_SERVICE_ERROR,
            f"AI出题服务异常: {str(e)}"
        )

