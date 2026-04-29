"""
全局异常处理器
统一处理项目中的异常，提供一致的错误响应格式
"""

import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from .exceptions import BaseCustomException, map_exception_to_http

logger = logging.getLogger(__name__)


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """自定义异常处理器"""
    
    # 记录异常日志
    logger.error(
        f"Custom exception occurred: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "error_message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
        },
        exc_info=True
    )
    
    # 转换为HTTP异常
    http_exc = map_exception_to_http(exc)
    
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """HTTP异常处理器"""
    
    # 记录异常日志
    logger.warning(
        f"HTTP exception occurred: {exc.status_code}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    # 统一错误响应格式
    error_detail = {
        "error_code": f"HTTP_{exc.status_code}",
        "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        "details": {}
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail,
        headers=getattr(exc, 'headers', None)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    
    # 记录异常日志
    logger.error(
        f"Unhandled exception occurred: {type(exc).__name__}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "traceback": traceback.format_exc(),
        },
        exc_info=True
    )
    
    # 返回通用错误响应
    error_detail = {
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "服务器内部错误，请稍后重试",
        "details": {
            "exception_type": type(exc).__name__
        }
    }
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )


def setup_exception_handlers(app):
    """设置异常处理器"""
    
    # 自定义异常处理器
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    
    # HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers have been set up successfully")
