"""
题目相关工具函数
提供题目内容标准化和哈希计算的统一实现
"""
import hashlib
import re

from app.common.exceptions import AppException, ErrorCode


def normalize_question_content(content: str) -> str:
    """
    题目内容标准化（统一逻辑）
    
    处理：
    1. 去除首尾空白
    2. 统一换行符
    3. 去除多余空白字符
    4. 统一全角/半角标点（可选）
    
    Args:
        content: 原始题目内容
        
    Returns:
        标准化后的题目内容
    """
    if not content:
        return ""
    
    # 去除首尾空白
    normalized = content.strip()
    
    # 统一换行符为 \n
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    
    # 去除多余空白行（保留单个换行）
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    
    # 去除行首行尾空白
    lines = [line.strip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    
    return normalized


def calculate_content_hash(content: str) -> str:
    """
    计算题目内容的 SHA256 哈希值（统一逻辑）
    
    Args:
        content: 标准化后的题目内容
        
    Returns:
        64位十六进制哈希字符串
        
    Raises:
        AppException: 当内容为空时
    """
    if not content:
        raise AppException(
            code=ErrorCode.PARAM_ERROR,
            message="题目内容不能为空"
        )
    
    hash_obj = hashlib.sha256(content.encode("utf-8"))
    return hash_obj.hexdigest()

