"""
安全防护模块
包含请求限流、输入验证、API密钥管理等安全功能
"""

import time
import hashlib
import re
from typing import Dict, Optional, Callable, Any
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import logging
import bleach
from urllib.parse import quote

from .exceptions import RateLimitError, ValidationError, AuthenticationError

logger = logging.getLogger(__name__)


class RateLimiter:
    """请求限流器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理过期的请求记录
        request_times = self.requests[identifier]
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # 检查是否超过限制
        if len(request_times) >= self.max_requests:
            # 计算重试时间
            oldest_request = request_times[0]
            retry_after = int(oldest_request + self.window_seconds - now) + 1
            return False, retry_after
        
        # 记录当前请求
        request_times.append(now)
        return True, None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求限流中间件"""
    
    def __init__(
        self,
        app,
        default_max_requests: int = 100,
        default_window_seconds: int = 60,
        rate_limit_rules: Optional[Dict[str, Dict[str, int]]] = None
    ):
        super().__init__(app)
        self.default_limiter = RateLimiter(default_max_requests, default_window_seconds)
        self.rate_limit_rules = rate_limit_rules or {}
        self.path_limiters: Dict[str, RateLimiter] = {}
        
        # 为特定路径创建限流器
        for path_pattern, config in self.rate_limit_rules.items():
            self.path_limiters[path_pattern] = RateLimiter(
                max_requests=config.get('max_requests', default_max_requests),
                window_seconds=config.get('window_seconds', default_window_seconds)
            )
    
    def get_client_identifier(self, request: Request) -> str:
        """获取客户端标识符"""
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        if api_key:
            token = api_key.replace('Bearer', '').strip()
            return f"api_key:{hashlib.md5(token.encode()).hexdigest()}"
        
        # 使用IP地址作为标识符
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        return f"ip:{client_ip}"
    
    def get_limiter_for_path(self, path: str) -> RateLimiter:
        """根据路径获取对应的限流器"""
        for path_pattern, limiter in self.path_limiters.items():
            if re.match(path_pattern, path):
                return limiter
        return self.default_limiter
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        try:
            # 获取客户端标识符
            client_id = self.get_client_identifier(request)
            
            # 获取对应的限流器
            limiter = self.get_limiter_for_path(request.url.path)
            
            # 检查是否允许请求
            allowed, retry_after = limiter.is_allowed(client_id)
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for client: {client_id}",
                    extra={
                        "client_id": client_id,
                        "path": request.url.path,
                        "method": request.method,
                        "retry_after": retry_after
                    }
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error_code": "RATE_LIMIT_ERROR",
                        "message": "请求过于频繁，请稍后再试",
                        "details": {"retry_after": retry_after}
                    },
                    headers={"Retry-After": str(retry_after or 0)}
                )
            
            # 继续处理请求
            response = await call_next(request)
            return response
            
        except RateLimitError:
            return JSONResponse(status_code=429, content={"error_code": "RATE_LIMIT_ERROR", "message": "请求过于频繁，请稍后再试"})
        except Exception as e:
            logger.error(f"Rate limit middleware error: {str(e)}", exc_info=True)
            # 如果限流中间件出错，允许请求继续
            return await call_next(request)


class InputValidator:
    """输入验证器"""
    
    # 常见的危险模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS脚本
        r'javascript:',  # JavaScript协议
        r'on\w+\s*=',  # 事件处理器
        r'expression\s*\(',  # CSS表达式
        r'@import',  # CSS导入
        r'<iframe[^>]*>',  # iframe标签
        r'<object[^>]*>',  # object标签
        r'<embed[^>]*>',  # embed标签
    ]
    
    # SQL注入模式
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
        r'(--|#|/\*|\*/)',
        r'(\bUNION\s+SELECT\b)',
    ]
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """清理HTML内容"""
        if not text:
            return text
        
        # 允许的HTML标签和属性
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attributes = {}
        
        # 使用bleach清理HTML
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return cleaned
    
    @classmethod
    def validate_input(cls, text: str, field_name: str = "input") -> str:
        """验证和清理用户输入"""
        if not text:
            return text
        
        # 检查危险模式
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(
                    f"Dangerous pattern detected in {field_name}: {pattern}",
                    extra={"field": field_name, "pattern": pattern}
                )
                raise ValidationError(
                    message=f"输入内容包含不安全的字符或模式",
                    field=field_name,
                    details={"pattern": pattern}
                )
        
        # 检查SQL注入模式
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(
                    f"SQL injection pattern detected in {field_name}: {pattern}",
                    extra={"field": field_name, "pattern": pattern}
                )
                raise ValidationError(
                    message=f"输入内容包含可疑的SQL模式",
                    field=field_name,
                    details={"pattern": pattern}
                )
        
        # 清理HTML内容
        cleaned_text = cls.sanitize_html(text)
        
        # URL编码特殊字符
        cleaned_text = quote(cleaned_text, safe=' -_.~')
        
        return cleaned_text
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(
                message="邮箱格式不正确",
                field="email"
            )
        return email.lower()
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """验证手机号格式"""
        # 中国手机号格式
        phone_pattern = r'^1[3-9]\d{9}$'
        cleaned_phone = re.sub(r'[^\d]', '', phone)
        
        if not re.match(phone_pattern, cleaned_phone):
            raise ValidationError(
                message="手机号格式不正确",
                field="phone"
            )
        return cleaned_phone


class APIKeyManager:
    """API密钥管理器"""
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """验证API密钥格式"""
        if not api_key:
            return False
        
        # API密钥应该是32-128个字符的字母数字字符串
        if not re.match(r'^[a-zA-Z0-9_-]{32,128}$', api_key):
            return False
        
        return True
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """对API密钥进行哈希处理"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(request: Request, required: bool = True) -> Optional[str]:
        """验证API密钥"""
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            if required:
                raise AuthenticationError(
                    message="缺少API密钥",
                    details={"header": "X-API-Key"}
                )
            return None
        
        if not APIKeyManager.validate_api_key_format(api_key):
            raise AuthenticationError(
                message="API密钥格式不正确",
                details={"format": "32-128个字母数字字符"}
            )
        
        # 这里可以添加数据库验证逻辑
        # 目前只验证格式
        
        return api_key


class SecurityHeadersMiddleware:
    """安全响应头中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # 添加安全响应头
                    security_headers = {
                        b"x-content-type-options": b"nosniff",
                        b"x-frame-options": b"DENY",
                        b"x-xss-protection": b"1; mode=block",
                        b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                        b"content-security-policy": b"default-src 'self'",
                        b"referrer-policy": b"strict-origin-when-cross-origin",
                        b"permissions-policy": b"geolocation=(), microphone=(), camera=()"
                    }
                    
                    # 更新响应头
                    for key, value in security_headers.items():
                        headers[key] = value
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def setup_security_middleware(app, rate_limit_config: Optional[Dict] = None):
    """设置安全中间件"""
    
    # 默认限流配置
    default_config = {
        'default_max_requests': 100,
        'default_window_seconds': 60,
        'rate_limit_rules': {
            r'/api/v1/chat.*': {'max_requests': 20, 'window_seconds': 60},
            r'/api/v1/upload.*': {'max_requests': 10, 'window_seconds': 60},
            r'/api/v1/auth.*': {'max_requests': 5, 'window_seconds': 300},
        }
    }
    
    config = {**default_config, **(rate_limit_config or {})}
    
    # 添加限流中间件
    app.add_middleware(
        RateLimitMiddleware,
        default_max_requests=config['default_max_requests'],
        default_window_seconds=config['default_window_seconds'],
        rate_limit_rules=config['rate_limit_rules']
    )
    
    # 添加安全响应头中间件
    app.add_middleware(SecurityHeadersMiddleware)
    
    logger.info("Security middleware has been set up successfully")