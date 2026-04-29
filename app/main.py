"""
智能电商客服与销售支持系统 - 主应用入口
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import json
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import traceback
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exception_handler import setup_exception_handlers
from app.core.security import setup_security_middleware, InputValidator, APIKeyManager
from app.core.auth import decode_access_token
from app.api.mutil_agent import (
    process_customer_query, 
    stream_customer_query,
    get_user_memory_summary,
    clear_user_memory
)
from app.mcp.tool_manager import (
    initialize_tools, 
    cleanup_tools, 
    get_tools_info,
    tool_manager
)
from app.api.database_endpoints import router as database_router

# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 初始化HTTP Bearer安全方案
security = HTTPBearer(auto_error=False)

# API密钥或JWT验证依赖
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    验证Bearer令牌：支持API密钥或JWT访问令牌
    """
    if not credentials:
        from app.core.exceptions import AuthenticationError
        raise AuthenticationError("缺少认证令牌")

    token = credentials.credentials
    if APIKeyManager.validate_api_key_format(token):
        return token

    payload = decode_access_token(token)
    if payload and payload.get("sub"):
        return token

    from app.core.exceptions import AuthenticationError
    raise AuthenticationError("无效的认证令牌")

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动应用...")
    try:
        await initialize_tools()
        logger.info("MCP工具初始化完成")
    except Exception as e:
        logger.error(f"MCP工具初始化失败: {e}")
        # 可以选择是否继续启动应用
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭应用...")
    try:
        await cleanup_tools()
        logger.info("MCP工具清理完成")
    except Exception as e:
        logger.error(f"MCP工具清理失败: {e}")

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于多智能体架构的智能电商客服与销售支持系统",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 添加CORS中间件
# 根据环境配置CORS策略
if settings.DEBUG:
    # 开发环境：限定本地前端来源
    cors_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000"
    ]
    cors_allow_credentials = True
else:
    # 生产环境：限制具体域名，但也允许本地测试
    cors_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://admin.yourdomain.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    cors_allow_credentials = True

cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
cors_headers = [
    "Accept",
    "Accept-Language",
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Origin"
]

logger.info(f"CORS Configuration - DEBUG: {settings.DEBUG}")
logger.info(f"CORS Origins: {cors_origins}")
logger.info(f"CORS Allow Credentials: {cors_allow_credentials}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
    max_age=600,
)

# 设置安全中间件
setup_security_middleware(app)

# 设置异常处理器
setup_exception_handlers(app)

# 注意：异常处理器已通过 setup_exception_handlers 函数设置

# 注册数据库相关路由
app.include_router(database_router)
from app.api.auth_endpoints import router as auth_router
app.include_router(auth_router)

# 请求模型
class CustomerQueryRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class MemoryRequest(BaseModel):
    user_id: str

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# 客户查询处理端点
@app.post("/api/v1/chat")
async def chat_with_customer_service(
    request: CustomerQueryRequest,
    api_key: str = Depends(verify_api_key)
):
    logger.info(f"收到客户查询请求: user_id={request.user_id}, message={request.message[:100]}...")
    cleaned_message = InputValidator.validate_input(request.message, "message")

    async def event_generator():
        try:
            async for chunk in stream_customer_query(
                user_message=cleaned_message,
                user_id=request.user_id,
                session_id=request.session_id
            ):
                try:
                    if isinstance(chunk, dict):
                        for node, update in chunk.items():
                            if isinstance(update, dict) and "final_response" in update:
                                final_text = update.get("final_response") or ""
                                for ch in final_text:
                                    yield {"event": "token", "data": json.dumps({"text": ch}, ensure_ascii=False)}
                                yield {"event": "end", "data": json.dumps({"final": final_text, "node": node}, ensure_ascii=False)}
                            else:
                                safe_update = {}
                                if isinstance(update, dict):
                                    for k, v in update.items():
                                        if k == "messages" and isinstance(v, list):
                                            safe_update[k] = [{"content": getattr(m, "content", str(m))} for m in v]
                                        elif isinstance(v, (str, int, float, bool)) or v is None:
                                            safe_update[k] = v
                                        else:
                                            try:
                                                json.dumps(v)
                                                safe_update[k] = v
                                            except Exception:
                                                safe_update[k] = str(v)
                                payload = {node: safe_update if safe_update else update}
                                yield {"event": "chunk", "data": json.dumps(payload, ensure_ascii=False)}
                    else:
                        yield {"event": "chunk", "data": json.dumps({"data": str(chunk)}, ensure_ascii=False)}
                except Exception as ser_err:
                    yield {"event": "error", "data": json.dumps({"message": str(ser_err)}, ensure_ascii=False)}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())

# 流式聊天端点
@app.post("/api/v1/chat/stream")
async def stream_chat_with_customer_service(
    request: CustomerQueryRequest,
    api_key: str = Depends(verify_api_key)
):
    logger.info(f"收到流式查询请求: user_id={request.user_id}, message={request.message[:100]}...")
    cleaned_message = InputValidator.validate_input(request.message, "message")

    async def event_generator():
        try:
            async for chunk in stream_customer_query(
                user_message=cleaned_message,
                user_id=request.user_id,
                session_id=request.session_id
            ):
                try:
                    if isinstance(chunk, dict):
                        cleaned = {}
                        for k, v in chunk.items():
                            if k == "messages" and isinstance(v, list):
                                cleaned[k] = [{"content": getattr(m, "content", str(m))} for m in v]
                            elif isinstance(v, (str, int, float, bool)) or v is None:
                                cleaned[k] = v
                            else:
                                try:
                                    json.dumps(v)
                                    cleaned[k] = v
                                except Exception:
                                    cleaned[k] = str(v)
                        payload = cleaned
                    else:
                        payload = {"data": str(chunk)}
                    yield {"event": "chunk", "data": json.dumps(payload, ensure_ascii=False)}
                except Exception as ser_err:
                    yield {"event": "error", "data": json.dumps({"message": str(ser_err)}, ensure_ascii=False)}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())

@app.get("/api/v1/chat/stream")
async def stream_chat_with_customer_service_sse(
    message: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    token: str = Query(...)
):
    if not APIKeyManager.validate_api_key_format(token):
        from app.core.exceptions import AuthenticationError
        raise AuthenticationError("无效的API密钥")
    cleaned_message = InputValidator.validate_input(message, "message")

    async def event_generator():
        try:
            async for chunk in stream_customer_query(
                user_message=cleaned_message,
                user_id=user_id,
                session_id=session_id
            ):
                try:
                    if isinstance(chunk, dict):
                        cleaned = {}
                        for k, v in chunk.items():
                            if k == "messages" and isinstance(v, list):
                                cleaned[k] = [{"content": getattr(m, "content", str(m))} for m in v]
                            elif isinstance(v, (str, int, float, bool)) or v is None:
                                cleaned[k] = v
                            else:
                                try:
                                    json.dumps(v)
                                    cleaned[k] = v
                                except Exception:
                                    cleaned[k] = str(v)
                        payload = cleaned
                    else:
                        payload = {"data": str(chunk)}
                    yield {"event": "chunk", "data": json.dumps(payload, ensure_ascii=False)}
                except Exception as ser_err:
                    yield {"event": "error", "data": json.dumps({"message": str(ser_err)}, ensure_ascii=False)}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())

# 用户记忆管理端点
@app.get("/api/v1/memory/{user_id}")
async def get_user_memory(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    获取用户记忆摘要
    """
    # 验证用户ID
    validated_user_id = InputValidator.validate_input(user_id, "user_id")
    
    result = await get_user_memory_summary(validated_user_id)
    return result

@app.delete("/api/v1/memory/{user_id}")
async def delete_user_memory(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    清除用户记忆
    """
    # 验证用户ID
    validated_user_id = InputValidator.validate_input(user_id, "user_id")
    
    result = await clear_user_memory(validated_user_id)
    return result

# 系统信息端点
@app.get("/api/v1/system/info")
async def get_system_info():
    """
    获取系统信息
    """
    logger.info("获取系统信息")
    
    # 获取MCP工具信息
    tools_info = get_tools_info()
    
    # 获取工具健康状态
    try:
        health_status = await tool_manager.health_check()
    except Exception as e:
        health_status = {"status": "error", "error": str(e)}
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "mcp_tools": tools_info,
        "mcp_health": health_status,
        "timestamp": "2024-10-15T10:00:00Z"
    }

# ===== MCP工具管理API =====

@app.get("/api/v1/tools")
async def get_available_tools(category: Optional[str] = None):
    """获取可用的MCP工具列表"""
    logger.info(f"获取可用工具列表，分类: {category}")
    
    try:
        if category:
            tools = tool_manager.get_tools_by_category(category)
        else:
            tools = tool_manager.get_all_tools()
        
        tool_list = []
        for tool in tools:
            tool_list.append({
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args if hasattr(tool, 'args') else {}
            })
        
        return {
            "success": True,
            "data": {
                "tools": tool_list,
                "count": len(tool_list),
                "category": category
            }
        }
    except Exception as e:
        logger.error(f"获取工具列表失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/v1/tools/categories")
async def get_tool_categories():
    """获取工具分类信息"""
    logger.info("获取工具分类信息")
    
    try:
        tools_info = get_tools_info()
        return {
            "success": True,
            "data": tools_info["categories"]
        }
    except Exception as e:
        logger.error(f"获取工具分类失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/v1/tools/{tool_name}/call")
async def call_tool_endpoint(
    tool_name: str, 
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """调用指定的MCP工具"""
    logger.info(f"调用工具: {tool_name}，参数: {request}")
    
    try:
        result = await tool_manager.call_tool(tool_name, **request)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        logger.error(f"工具调用失败 - 工具不存在: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/v1/tools/health")
async def check_tools_health():
    """检查MCP工具健康状态"""
    logger.info("检查MCP工具健康状态")
    
    try:
        health_status = await tool_manager.health_check()
        return {
            "success": True,
            "data": health_status
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
