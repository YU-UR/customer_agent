"""
自定义异常类体系
提供项目中各种业务场景的异常处理
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
from starlette import status


class BaseCustomException(Exception):
    """基础自定义异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details or {}
        )
        if field:
            self.details["field"] = field


class DatabaseError(BaseCustomException):
    """数据库操作异常"""
    
    def __init__(self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class ExternalServiceError(BaseCustomException):
    """外部服务调用异常"""
    
    def __init__(
        self,
        message: str,
        service_name: str = None,
        status_code: int = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details or {}
        )
        if service_name:
            self.details["service_name"] = service_name
        if status_code:
            self.details["status_code"] = status_code


class AuthenticationError(BaseCustomException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details or {}
        )


class AuthorizationError(BaseCustomException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details or {}
        )


class RateLimitError(BaseCustomException):
    """请求限流异常"""
    
    def __init__(
        self,
        message: str = "请求过于频繁，请稍后再试",
        retry_after: int = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details or {}
        )
        if retry_after:
            self.details["retry_after"] = retry_after


class ConfigurationError(BaseCustomException):
    """配置错误异常"""
    
    def __init__(self, message: str, config_key: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details or {}
        )
        if config_key:
            self.details["config_key"] = config_key


class BusinessLogicError(BaseCustomException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, business_code: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details or {}
        )
        if business_code:
            self.details["business_code"] = business_code


class ResourceNotFoundError(BaseCustomException):
    """资源未找到异常"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details or {}
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class AgentError(BaseCustomException):
    """智能体相关异常"""
    
    def __init__(self, message: str, agent_type: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            details=details or {}
        )
        if agent_type:
            self.details["agent_type"] = agent_type


class RAGError(BaseCustomException):
    """RAG系统异常"""
    
    def __init__(self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RAG_ERROR",
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class MCPError(BaseCustomException):
    """MCP工具异常"""
    
    def __init__(self, message: str, tool_name: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="MCP_ERROR",
            details=details or {}
        )
        if tool_name:
            self.details["tool_name"] = tool_name


# HTTP异常映射
def map_exception_to_http(exception: BaseCustomException) -> HTTPException:
    """将自定义异常映射为HTTP异常"""
    
    status_code_mapping = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "RATE_LIMIT_ERROR": status.HTTP_429_TOO_MANY_REQUESTS,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
        "CONFIGURATION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "BUSINESS_LOGIC_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "AGENT_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "RAG_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "MCP_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_mapping.get(exception.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    detail = {
        "error_code": exception.error_code,
        "message": exception.message,
        "details": exception.details
    }
    
    headers = {}
    if exception.error_code == "RATE_LIMIT_ERROR" and "retry_after" in exception.details:
        headers["Retry-After"] = str(exception.details["retry_after"])
    
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers if headers else None
    )