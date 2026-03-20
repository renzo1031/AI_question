"""
请求日志中间件
记录每个HTTP请求的详细信息
"""
import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        # 请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        
        # 记录请求开始
        logger.info(
            f"Request: {method} {path}"
            + (f"?{query_params}" if query_params else "")
            + f" | IP: {client_ip}"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {method} {path} | "
                f"Error: {str(e)} | "
                f"Time: {process_time:.2f}ms"
            )
            raise
        
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        
        # 记录响应
        status_code = response.status_code
        log_message = (
            f"Response: {method} {path} | "
            f"Status: {status_code} | "
            f"Time: {process_time:.2f}ms"
        )
        
        # 根据状态码使用不同日志级别
        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        return response

