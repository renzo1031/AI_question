"""
统一响应格式模块
所有API接口返回统一的响应格式
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型
    
    Attributes:
        code: 业务状态码，0表示成功，其他表示失败
        message: 响应消息
        data: 响应数据
    """
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PageInfo(BaseModel):
    """分页信息"""
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 0


class PageResponseModel(BaseModel, Generic[T]):
    """
    分页响应模型
    """
    code: int = 0
    message: str = "success"
    data: Optional[list[T]] = None
    page_info: Optional[PageInfo] = None


def success(data: Any = None, message: str = "success") -> dict:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        
    Returns:
        统一格式的响应字典
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error(
    code: int = 1, 
    message: str = "error", 
    data: Any = None
) -> dict:
    """
    错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        data: 额外数据
        
    Returns:
        统一格式的响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def page_success(
    data: list,
    page: int,
    page_size: int,
    total: int,
    message: str = "success"
) -> dict:
    """
    分页成功响应
    
    Args:
        data: 数据列表
        page: 当前页码
        page_size: 每页大小
        total: 总数量
        message: 响应消息
        
    Returns:
        统一格式的分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "code": 0,
        "message": message,
        "data": data,
        "page_info": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

