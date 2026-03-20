"""
全局异常处理器
统一处理所有异常并返回标准响应格式
"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.common.exceptions import AppException, ErrorCode
from app.common.response import error


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    应用自定义异常处理器
    """
    logger.warning(
        f"AppException: code={exc.code}, message={exc.message}, "
        f"path={request.url.path}"
    )
    return JSONResponse(
        status_code=exc.http_status,
        content=error(code=exc.code, message=exc.message, data=exc.data)
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    请求验证异常处理器
    """
    # 尝试读取请求体以便调试
    try:
        body = await request.body()
        logger.warning(f"Request body (raw): {body[:500]}")  # 只记录前500字节
    except Exception as e:
        logger.warning(f"Failed to read request body: {e}")
    
    errors = exc.errors()
    error_messages = []
    cleaned_errors = []
    
    for err in errors:
        # 获取字段名，跳过'body'
        loc = err.get("loc", ())
        field = ".".join(str(loc_item) for loc_item in loc[1:]) if len(loc) > 1 else ""
        msg = err.get("msg", "")
        if field:
            error_messages.append(f"{field}: {msg}")
        else:
            error_messages.append(msg)
        
        # 清理错误信息，只保留可以JSON序列化的基本类型
        # 将loc转换为字符串列表，确保可序列化
        cleaned_loc = [str(loc_item) for loc_item in loc] if loc else []
        
        cleaned_err = {
            "type": str(err.get("type", "")),
            "loc": cleaned_loc,
            "msg": str(msg),
        }
        cleaned_errors.append(cleaned_err)
    
    message = "; ".join(error_messages) if error_messages else "参数验证失败"
    
    logger.warning(
        f"ValidationError: {message}, path={request.url.path}"
    )
    
    return JSONResponse(
        status_code=422,
        content=error(
            code=ErrorCode.PARAM_ERROR,
            message=message,
            data={"errors": cleaned_errors}
        )
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    """
    logger.exception(
        f"UnhandledException: {str(exc)}, path={request.url.path}"
    )
    return JSONResponse(
        status_code=500,
        content=error(
            code=ErrorCode.UNKNOWN_ERROR,
            message="服务器内部错误"
        )
    )

