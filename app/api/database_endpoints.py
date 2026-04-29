"""
数据库相关的API端点
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from app.services import (
    user_service,
    conversation_service,
    message_service,
    agent_output_service,
    integration_service
)

router = APIRouter(prefix="/api/v1/database", tags=["database"])


# ===== 用户相关接口 =====

@router.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """获取用户信息"""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": user.to_dict()}


@router.get("/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    status: Optional[str] = None
):
    """获取用户的会话列表"""
    conversations = conversation_service.get_user_conversations(
        user_id=user_id,
        limit=limit,
        status=status
    )
    return {
        "success": True,
        "data": [conv.to_dict() for conv in conversations],
        "count": len(conversations)
    }


# ===== 会话相关接口 =====

@router.get("/conversations/{session_id}")
async def get_conversation_info(session_id: str):
    """获取会话详情"""
    conversation = conversation_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "data": conversation.to_dict()}


@router.get("/conversations/{session_id}/messages")
async def get_conversation_messages(
    session_id: str,
    limit: Optional[int] = Query(default=None, ge=1, le=1000)
):
    """获取会话的所有消息"""
    messages = message_service.get_session_messages(session_id, limit)
    return {
        "success": True,
        "data": [msg.to_dict() for msg in messages],
        "count": len(messages)
    }


@router.get("/conversations/{session_id}/history")
async def get_conversation_history(session_id: str):
    """获取完整的会话历史（包括消息和智能体输出）"""
    result = await integration_service.get_conversation_history(session_id)
    return result


@router.post("/conversations/{session_id}/end")
async def end_conversation(
    session_id: str,
    satisfaction_score: Optional[int] = Query(default=None, ge=1, le=5),
    feedback: Optional[str] = None
):
    """结束会话并提交评分"""
    user_id = conversation_service.get_conversation(session_id)
    if not user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    result = await integration_service.record_conversation_end(
        session_id=session_id,
        user_id=user_id.user_id,
        satisfaction_score=satisfaction_score,
        feedback=feedback
    )
    return result


# ===== 消息相关接口 =====

@router.get("/messages/{message_id}")
async def get_message_info(message_id: str):
    """获取消息详情"""
    message = message_service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"success": True, "data": message.to_dict()}


@router.post("/messages/{message_id}/rating")
async def rate_message(
    message_id: str,
    rating: int = Query(..., ge=1, le=5),
    rating_reason: Optional[str] = None
):
    """给消息评分"""
    message = message_service.update_message_rating(
        message_id=message_id,
        rating=rating,
        rating_reason=rating_reason
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"success": True, "data": message.to_dict()}


class MessageFeedbackRequest(BaseModel):
    feedback_type: str  # like, dislike, helpful, not_helpful, report
    feedback_text: Optional[str] = None
    tags: Optional[List[str]] = None
    issue_category: Optional[str] = None


@router.post("/messages/{message_id}/feedback")
async def submit_message_feedback(
    message_id: str,
    request: MessageFeedbackRequest
):
    """提交消息反馈"""
    # 获取消息信息
    message = message_service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    feedback = message_service.create_message_feedback(
        message_id=message_id,
        user_id=message.user_id,
        session_id=message.session_id,
        feedback_type=request.feedback_type,
        feedback_text=request.feedback_text,
        tags=request.tags,
        issue_category=request.issue_category
    )
    
    return {"success": True, "data": {"feedback_id": feedback.id}}


# ===== 智能体输出相关接口 =====

@router.get("/agent-outputs/{session_id}")
async def get_agent_outputs(session_id: str):
    """获取会话的所有智能体输出"""
    outputs = agent_output_service.get_session_agent_outputs(session_id)
    return {
        "success": True,
        "data": [output.to_dict() for output in outputs],
        "count": len(outputs)
    }


@router.get("/agent-outputs/{session_id}/router")
async def get_router_decisions(session_id: str):
    """获取路由决策记录"""
    outputs = agent_output_service.get_router_decisions(session_id)
    return {
        "success": True,
        "data": [output.to_dict() for output in outputs],
        "count": len(outputs)
    }


@router.get("/agent-outputs/{session_id}/{agent_type}")
async def get_agent_outputs_by_type(session_id: str, agent_type: str):
    """获取指定类型的智能体输出"""
    outputs = agent_output_service.get_agent_outputs_by_type(session_id, agent_type)
    return {
        "success": True,
        "data": [output.to_dict() for output in outputs],
        "count": len(outputs)
    }


# ===== 统计相关接口 =====

@router.get("/statistics/agent/{agent_type}")
async def get_agent_statistics(
    agent_type: str,
    days: int = Query(default=7, ge=1, le=90)
):
    """获取智能体统计数据"""
    stats = agent_output_service.get_agent_statistics(agent_type, days)
    return {"success": True, "data": stats}


@router.get("/statistics/conversation/{session_id}")
async def get_conversation_statistics(session_id: str):
    """获取会话统计信息"""
    conversation = conversation_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 获取消息统计
    messages = message_service.get_session_messages(session_id)
    user_messages = [m for m in messages if m.role == 'user']
    agent_messages = [m for m in messages if m.role == 'assistant']
    
    # 获取智能体输出统计
    agent_outputs = agent_output_service.get_session_agent_outputs(session_id)
    
    return {
        "success": True,
        "data": {
            "conversation": conversation.to_dict(),
            "message_count": len(messages),
            "user_message_count": len(user_messages),
            "agent_message_count": len(agent_messages),
            "agent_output_count": len(agent_outputs),
            "total_tokens": conversation.total_tokens,
            "total_cost": conversation.total_cost,
            "duration": conversation.total_duration
        }
    }

