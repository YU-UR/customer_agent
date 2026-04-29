"""
消息服务 - 处理消息相关的业务逻辑
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.messages import Message, MessageFeedback
from app.db.session import get_db
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class MessageService:
    """消息服务类"""
    
    @staticmethod
    def create_message(session_id: str, user_id: str, role: str, content: str,
                      sequence: int, **kwargs) -> Message:
        """创建消息记录"""
        with get_db() as db:
            message = Message(
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=content,
                sequence=sequence,
                message_type=kwargs.get('message_type', 'text'),
                agent_type=kwargs.get('agent_type'),
                agent_name=kwargs.get('agent_name'),
                router_confidence=kwargs.get('router_confidence'),
                user_intent=kwargs.get('user_intent'),
                processing_time=kwargs.get('processing_time'),
                response_time=kwargs.get('response_time'),
                token_usage=kwargs.get('token_usage'),
                cost=kwargs.get('cost'),
                extra_data=kwargs.get('extra_data'),
                sent_at=datetime.now()
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            logger.info(f"Created message: {message.id} in session: {session_id}")
            return message
    
    @staticmethod
    def get_message(message_id: str) -> Optional[Message]:
        """获取消息"""
        with get_db() as db:
            message = db.query(Message).filter(Message.id == message_id).first()
            return message
    
    @staticmethod
    def get_session_messages(session_id: str, limit: Optional[int] = None) -> List[Message]:
        """获取会话的所有消息"""
        with get_db() as db:
            query = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.sequence)
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            return messages
    
    @staticmethod
    def get_last_messages(session_id: str, count: int = 10) -> List[Message]:
        """获取最近的N条消息"""
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(desc(Message.sequence)).limit(count).all()
            
            # 反转顺序以按时间正序返回
            return list(reversed(messages))
    
    @staticmethod
    def update_message_rating(message_id: str, rating: int, 
                             rating_reason: Optional[str] = None) -> Optional[Message]:
        """更新消息评分"""
        with get_db() as db:
            message = db.query(Message).filter(Message.id == message_id).first()
            
            if not message:
                return None
            
            message.rating = rating
            if rating_reason:
                message.rating_reason = rating_reason
            
            db.commit()
            db.refresh(message)
            
            return message
    
    @staticmethod
    def create_message_feedback(message_id: str, user_id: str, feedback_type: str,
                               **kwargs) -> MessageFeedback:
        """创建消息反馈"""
        with get_db() as db:
            feedback = MessageFeedback(
                message_id=message_id,
                user_id=user_id,
                session_id=kwargs.get('session_id'),
                feedback_type=feedback_type,
                feedback_text=kwargs.get('feedback_text'),
                tags=kwargs.get('tags'),
                issue_category=kwargs.get('issue_category'),
                severity=kwargs.get('severity')
            )
            
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            logger.info(f"Created feedback for message: {message_id}")
            return feedback
    
    @staticmethod
    def get_message_feedbacks(message_id: str) -> List[MessageFeedback]:
        """获取消息的所有反馈"""
        with get_db() as db:
            feedbacks = db.query(MessageFeedback).filter(
                MessageFeedback.message_id == message_id
            ).all()
            return feedbacks
    
    @staticmethod
    def get_next_sequence(session_id: str) -> int:
        """获取会话中下一个消息序号"""
        with get_db() as db:
            last_message = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(desc(Message.sequence)).first()
            
            if last_message:
                return last_message.sequence + 1
            return 1


# 全局单例
message_service = MessageService()

