"""操作日志相关的数据模型"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OperationLogResponse(BaseModel):
    """操作日志响应模型"""
    
    id: int = Field(..., description="日志ID")
    user_type: str = Field(..., description="用户类型：admin/user")
    user_id: Optional[UUID] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    log_level: str = Field(..., description="日志级别")
    module: str = Field(..., description="所属模块")
    action: str = Field(..., description="操作动作")
    description: Optional[str] = Field(None, description="操作描述")
    request_method: Optional[str] = Field(None, description="HTTP请求方法")
    request_path: Optional[str] = Field(None, description="请求路径")
    request_params: Optional[dict] = Field(None, description="请求参数")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="User-Agent")
    status_code: Optional[int] = Field(None, description="HTTP状态码")
    is_success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    response_time_ms: Optional[int] = Field(None, description="响应时间(毫秒)")
    extra_data: Optional[dict] = Field(None, description="额外数据")
    created_at: datetime = Field(..., description="创建时间")
    
    @field_validator('ip_address', mode='before')
    @classmethod
    def convert_ip_address(cls, value):
        """将IP地址对象转换为字符串"""
        if value is None:
            return None
        # 处理 IPv4Address 或 IPv6Address 对象
        return str(value)
    
    class Config:
        from_attributes = True


class OperationLogListRequest(BaseModel):
    """操作日志列表查询请求"""
    
    user_type: Optional[str] = Field(None, description="用户类型：admin/user")
    user_id: Optional[UUID] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    log_level: Optional[str] = Field(None, description="日志级别")
    module: Optional[str] = Field(None, description="所属模块")
    action: Optional[str] = Field(None, description="操作动作（模糊搜索）")
    is_success: Optional[bool] = Field(None, description="是否成功")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class OperationLogListResponse(BaseModel):
    """操作日志列表响应"""
    
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list[OperationLogResponse] = Field(..., description="日志列表")
