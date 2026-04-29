"""
会话服务 - 处理会话相关的业务逻辑
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.conversation import Conversation
from app.db.session import get_db
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class ConversationService:
    """会话服务类"""
    
    @staticmethod
    def create_conversation(session_id: str, user_id: str, first_question: str, 
                          **kwargs) -> Conversation:
        """创建新会话"""
        with get_db() as db:
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id,
                first_question=first_question,
                title=kwargs.get('title', first_question[:50]),  # 默认使用前50字符作为标题
                status='active',
                started_at=datetime.now(),
                last_activity_at=datetime.now()
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Created conversation: {session_id} for user: {user_id}")
            return conversation
    
    @staticmethod
    def get_conversation(session_id: str) -> Optional[Conversation]:
        """获取会话信息"""
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            return conversation
    
    @staticmethod
    def get_or_create_conversation(session_id: str, user_id: str, 
                                   first_question: str) -> Conversation:
        """获取或创建会话"""
        conversation = ConversationService.get_conversation(session_id)
        
        if conversation:
            # 更新最后活跃时间
            with get_db() as db:
                conv = db.query(Conversation).filter(
                    Conversation.session_id == session_id
                ).first()
                if conv:
                    conv.last_activity_at = datetime.now()
                    db.commit()
                    db.refresh(conv)
                    return conv
        
        return ConversationService.create_conversation(session_id, user_id, first_question)
    
    @staticmethod
    def update_conversation_stats(session_id: str, increment_messages: int = 1,
                                 increment_user_messages: int = 0,
                                 increment_agent_messages: int = 0,
                                 increment_switches: int = 0,
                                 agent_type: Optional[str] = None,
                                 last_message: Optional[str] = None) -> Optional[Conversation]:
        """更新会话统计信息"""
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            conversation.message_count += increment_messages
            conversation.user_message_count += increment_user_messages
            conversation.agent_message_count += increment_agent_messages
            conversation.agent_switches += increment_switches
            conversation.last_activity_at = datetime.now()
            
            if agent_type and not conversation.primary_agent:
                conversation.primary_agent = agent_type
            
            if last_message:
                conversation.last_message = last_message[:500]  # 限制长度
            
            db.commit()
            db.refresh(conversation)
            
            return conversation
    
    @staticmethod
    def update_conversation_category(session_id: str, category: str, 
                                    agent_type: str) -> Optional[Conversation]:
        """更新会话分类"""
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            if not conversation.category:
                # 根据智能体类型推断分类
                category_mapping = {
                    'order_agent': 'order',
                    'product_agent': 'product',
                    'after_sales_agent': 'after_sales',
                    'promotion_agent': 'promotion',
                    'general_agent': 'general'
                }
                conversation.category = category_mapping.get(agent_type, 'general')
            
            if not conversation.primary_agent:
                conversation.primary_agent = agent_type
            
            db.commit()
            db.refresh(conversation)
            
            return conversation
    
    @staticmethod
    def end_conversation(session_id: str, satisfaction_score: Optional[int] = None,
                        feedback: Optional[str] = None) -> Optional[Conversation]:
        """结束会话"""
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            conversation.status = 'closed'
            conversation.ended_at = datetime.now()
            
            if satisfaction_score:
                conversation.satisfaction_score = satisfaction_score
                conversation.feedback_time = datetime.now()
            
            if feedback:
                conversation.feedback = feedback
            
            # 计算会话总时长
            if conversation.started_at:
                duration = (conversation.ended_at - conversation.started_at).total_seconds()
                conversation.total_duration = duration
            
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Ended conversation: {session_id}")
            return conversation
    
    @staticmethod
    def update_token_cost(session_id: str, tokens: int, cost: float) -> Optional[Conversation]:
        """更新Token和成本统计"""
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            conversation.total_tokens += tokens
            conversation.total_cost += cost
            
            db.commit()
            db.refresh(conversation)
            
            return conversation
    
    @staticmethod
    def get_user_conversations(user_id: str, limit: int = 10, 
                              status: Optional[str] = None) -> List[Conversation]:
        """获取用户的会话列表"""
        with get_db() as db:
            query = db.query(Conversation).filter(Conversation.user_id == user_id)
            
            if status:
                query = query.filter(Conversation.status == status)
            
            conversations = query.order_by(desc(Conversation.created_time)).limit(limit).all()
            return conversations
    
    @staticmethod
    def get_conversation_dict(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息（字典格式）"""
        conversation = ConversationService.get_conversation(session_id)
        if conversation:
            return conversation.to_dict()
        return None


# 全局单例
conversation_service = ConversationService()

