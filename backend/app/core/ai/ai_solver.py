"""
AI解题模块
负责调用大模型进行题目解析，并校验返回结果
"""
import json
import re
from typing import Optional

from loguru import logger

from app.common.exceptions import AppException, ErrorCode
from app.core.ai.manager import ai_model_manager
from app.core.ai.prompts import build_solve_question_prompt


async def call_llm(prompt: str, provider_name: Optional[str] = None) -> str:
    """
    调用大模型，返回原始文本响应
    
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
        
        # 调用提供商的 call_raw 方法，传入完整 prompt
        # 不传入 system_prompt，让提供商使用默认值或由 prompt 自行处理
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


def _extract_json_from_text(text: str) -> str:
    """
    从文本中提取JSON内容
    
    尝试从AI返回的文本中提取纯JSON部分，去除可能的自然语言前缀或后缀
    
    Args:
        text: 原始文本
        
    Returns:
        提取的JSON字符串
        
    Raises:
        AppException: 当无法提取有效JSON时
    """
    if not text or not text.strip():
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            "AI返回结果为空"
        )
    
    # 去除首尾空白
    text = text.strip()
    
    # 尝试直接解析（如果已经是纯JSON）
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # 尝试提取JSON对象（使用正则表达式）
    # 匹配 {...} 格式的JSON对象
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    if matches:
        # 尝试解析最长的匹配项（通常是完整的JSON）
        for match in sorted(matches, key=len, reverse=True):
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
    
    # 尝试提取代码块中的JSON（```json ... ``` 或 ``` ... ```）
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    code_matches = re.findall(code_block_pattern, text, re.DOTALL)
    if code_matches:
        for match in code_matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
    
    # 如果都失败了，抛出异常
    raise AppException(
        ErrorCode.AI_JSON_PARSE_ERROR,
        f"无法从AI返回结果中提取有效JSON。返回内容: {text[:200]}..."
    )


def _validate_ai_response(data: dict) -> None:
    """
    校验AI返回的JSON数据是否包含所有必需字段
    
    Args:
        data: 解析后的JSON字典
        
    Raises:
        AppException: 当缺少必需字段或字段格式不正确时
    """
    required_fields = {
        "question_type": str,
        "subject": str,
        "difficulty": int,
        "answer": str,
        "analysis": str,
        "options": list
    }
    
    # 检查必需字段是否存在
    missing_fields = []
    for field, field_type in required_fields.items():
        if field not in data:
            missing_fields.append(field)
        elif not isinstance(data[field], field_type):
            raise AppException(
                ErrorCode.AI_RESPONSE_INVALID,
                f"字段 '{field}' 类型错误，期望 {field_type.__name__}，实际 {type(data[field]).__name__}"
            )
    
    if missing_fields:
        raise AppException(
            ErrorCode.AI_RESPONSE_MISSING_FIELD,
            f"AI返回结果缺少必需字段: {', '.join(missing_fields)}"
        )
    
    # 校验字符串字段不能为空
    string_fields = ["question_type", "subject", "answer", "analysis"]
    for field in string_fields:
        if not data[field] or not data[field].strip():
            raise AppException(
                ErrorCode.AI_RESPONSE_INVALID,
                f"字段 '{field}' 不能为空"
            )
    
    # 校验 difficulty 范围
    difficulty = data["difficulty"]
    if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"字段 'difficulty' 必须是1-5之间的整数，实际值: {difficulty}"
        )
    
    # 校验 options 格式（如果是选择题，应该包含选项）
    options = data["options"]
    if not isinstance(options, list):
        raise AppException(
            ErrorCode.AI_RESPONSE_INVALID,
            f"字段 'options' 必须是数组，实际类型: {type(options).__name__}"
        )
    
    # 校验选项格式（如果options不为空）
    if options:
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                raise AppException(
                    ErrorCode.AI_RESPONSE_INVALID,
                    f"选项 {i} 必须是对象，实际类型: {type(option).__name__}"
                )
            if "option_key" not in option or "option_text" not in option:
                raise AppException(
                    ErrorCode.AI_RESPONSE_INVALID,
                    f"选项 {i} 缺少必需字段 'option_key' 或 'option_text'"
                )
            if not option["option_key"] or not option["option_text"]:
                raise AppException(
                    ErrorCode.AI_RESPONSE_INVALID,
                    f"选项 {i} 的 'option_key' 或 'option_text' 不能为空"
                )


async def solve_question(
    question_text: str,
    context: Optional[str] = None,
    provider_name: Optional[str] = None
) -> dict:
    """
    AI解题主函数
    
    接收OCR题干文本，调用大模型进行解析，并返回结构化的解题结果
    
    Args:
        question_text: OCR识别的题目文本
        context: 上下文信息（可选）
        provider_name: AI提供商名称（tongyi/deepseek/kimi），如果为None则使用配置的默认提供商
        
    Returns:
        解析后的题目信息字典，包含：
        {
            "question_type": str,      # 题目类型
            "subject": str,             # 科目
            "difficulty": int,          # 难度（1-5）
            "answer": str,              # 答案
            "analysis": str,            # 解析
            "options": list             # 选项列表
        }
        
    Raises:
        AppException: 当AI服务调用失败、JSON解析失败或数据校验失败时
    """
    if not question_text or not question_text.strip():
        raise AppException(
            ErrorCode.PARAM_ERROR,
            "题目文本不能为空"
        )
    
    try:
        # 1. 构建Prompt
        prompt = build_solve_question_prompt(question_text, context)
        logger.debug(f"构建的Prompt长度: {len(prompt)}")
        
        # 2. 调用大模型
        logger.info(f"开始调用AI模型解题，提供商: {provider_name or '默认'}...")
        ai_response = await call_llm(prompt, provider_name=provider_name)
        
        if not ai_response or not ai_response.strip():
            raise AppException(
                ErrorCode.AI_SERVICE_ERROR,
                "AI服务返回结果为空"
            )
        
        logger.debug(f"AI返回结果长度: {len(ai_response)}")
        logger.debug(f"AI返回结果预览: {ai_response[:200]}...")
        
        # 3. 提取JSON内容
        json_text = _extract_json_from_text(ai_response)
        logger.debug(f"提取的JSON: {json_text[:200]}...")
        
        # 4. 解析JSON
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}, JSON内容: {json_text[:500]}")
            raise AppException(
                ErrorCode.AI_JSON_PARSE_ERROR,
                f"AI返回的JSON格式无效: {str(e)}"
            )
        
        # 5. 校验数据
        _validate_ai_response(data)
        
        logger.info("AI解题成功")
        return data
        
    except AppException:
        # 重新抛出业务异常
        raise
    except Exception as e:
        # 捕获其他异常，转换为业务异常
        logger.error(f"AI解题过程发生异常: {str(e)}", exc_info=True)
        raise AppException(
            ErrorCode.AI_SERVICE_ERROR,
            f"AI解题服务异常: {str(e)}"
        )

