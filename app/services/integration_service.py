"""
集成服务 - 将智能体执行过程与数据库集成
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import time

from app.services.user_service import user_service
from app.services.conversation_service import conversation_service
from app.services.message_service import message_service
from app.services.agent_output_service import agent_output_service
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class IntegrationService:
    """
    集成服务 - 协调各个服务，记录完整的对话流程
    """
    
    @staticmethod
    async def record_conversation_start(session_id: str, user_id: str, 
                                       first_question: str) -> Dict[str, Any]:
        """记录会话开始"""
        try:
            # 1. 创建或获取用户
            user = user_service.create_or_get_user(user_id)
            
            # 2. 创建或获取会话
            conversation = conversation_service.get_or_create_conversation(
                session_id=session_id,
                user_id=user_id,
                first_question=first_question
            )
            
            # 3. 更新用户统计
            user_service.update_user_stats(user_id, increment_conversations=1)
            
            logger.info(f"Conversation started: {session_id}")
            
            return {
                'success': True,
                'user': user.to_dict() if hasattr(user, 'to_dict') else None,
                'conversation': conversation.to_dict() if hasattr(conversation, 'to_dict') else None
            }
            
        except Exception as e:
            logger.error(f"Error recording conversation start: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    async def record_user_message(session_id: str, user_id: str, 
                                  message: str) -> Optional[str]:
        """记录用户消息"""
        try:
            # 获取下一个序号
            sequence = message_service.get_next_sequence(session_id)
            
            # 创建消息记录
            msg = message_service.create_message(
                session_id=session_id,
                user_id=user_id,
                role='user',
                content=message,
                sequence=sequence,
                message_type='text'
            )
            
            # 更新会话统计
            conversation_service.update_conversation_stats(
                session_id=session_id,
                increment_messages=1,
                increment_user_messages=1,
                last_message=message
            )
            
            # 更新用户统计
            user_service.update_user_stats(user_id, increment_messages=1)
            
            return msg.id
            
        except Exception as e:
            logger.error(f"Error recording user message: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def record_router_decision(session_id: str, user_id: str, 
                                    input_text: str, router_result: Dict[str, Any],
                                    processing_time: float) -> Optional[str]:
        """记录路由决策"""
        try:
            execution_order = agent_output_service.get_next_execution_order(session_id)
            
            output = agent_output_service.create_agent_output(
                session_id=session_id,
                user_id=user_id,
                agent_type='router_agent',
                agent_name='路由智能体',
                input_text=input_text,
                output_text=f"路由到: {router_result.get('target_agent')}",
                execution_order=execution_order,
                processing_time=processing_time,
                target_agent=router_result.get('target_agent'),
                confidence=router_result.get('confidence'),
                user_intent=router_result.get('user_intent'),
                status='success'
            )
            
            # 更新会话分类
            conversation_service.update_conversation_category(
                session_id=session_id,
                category='',
                agent_type=router_result.get('target_agent')
            )
            
            return output.id
            
        except Exception as e:
            logger.error(f"Error recording router decision: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def record_agent_response(session_id: str, user_id: str, message_id: str,
                                   agent_type: str, agent_name: str,
                                   input_text: str, output_text: str,
                                   processing_time: float, **kwargs) -> Optional[str]:
        """记录智能体响应"""
        try:
            # 1. 记录智能体输出
            execution_order = agent_output_service.get_next_execution_order(session_id)
            
            output = agent_output_service.create_agent_output(
                session_id=session_id,
                message_id=message_id,
                user_id=user_id,
                agent_type=agent_type,
                agent_name=agent_name,
                input_text=input_text,
                output_text=output_text,
                execution_order=execution_order,
                processing_time=processing_time,
                input_tokens=kwargs.get('input_tokens'),
                output_tokens=kwargs.get('output_tokens'),
                total_tokens=kwargs.get('total_tokens'),
                cost=kwargs.get('cost'),
                tools_called=kwargs.get('tools_called'),
                memory_context=kwargs.get('memory_context'),
                memory_used=kwargs.get('memory_used', False),
                extra_data=kwargs.get('extra_data'),
                status='success'
            )
            
            # 2. 创建消息记录（助手回复）
            sequence = message_service.get_next_sequence(session_id)
            
            message_service.create_message(
                session_id=session_id,
                user_id=user_id,
                role='assistant',
                content=output_text,
                sequence=sequence,
                message_type='text',
                agent_type=agent_type,
                agent_name=agent_name,
                processing_time=processing_time,
                token_usage=kwargs.get('token_usage'),
                cost=kwargs.get('cost'),
                metadata=kwargs.get('metadata')
            )
            
            # 3. 更新会话统计
            conversation_service.update_conversation_stats(
                session_id=session_id,
                increment_messages=1,
                increment_agent_messages=1,
                agent_type=agent_type,
                last_message=output_text
            )
            
            # 4. 更新Token和成本
            if kwargs.get('total_tokens') and kwargs.get('cost'):
                conversation_service.update_token_cost(
                    session_id=session_id,
                    tokens=kwargs.get('total_tokens'),
                    cost=kwargs.get('cost')
                )
            
            # 5. 更新用户统计
            user_service.update_user_stats(user_id, increment_messages=1)
            
            return output.id
            
        except Exception as e:
            logger.error(f"Error recording agent response: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def record_conversation_end(session_id: str, user_id: str,
                                     satisfaction_score: Optional[int] = None,
                                     feedback: Optional[str] = None) -> Dict[str, Any]:
        """记录会话结束"""
        try:
            # 结束会话
            conversation = conversation_service.end_conversation(
                session_id=session_id,
                satisfaction_score=satisfaction_score,
                feedback=feedback
            )
            
            # 如果有满意度评分，更新用户平均满意度
            if satisfaction_score:
                user_service.update_user_satisfaction(user_id, satisfaction_score)
            
            logger.info(f"Conversation ended: {session_id}")
            
            return {
                'success': True,
                'conversation': conversation.to_dict() if conversation and hasattr(conversation, 'to_dict') else None
            }
            
        except Exception as e:
            logger.error(f"Error recording conversation end: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    async def get_conversation_history(session_id: str) -> Dict[str, Any]:
        """获取完整的会话历史"""
        try:
            # 获取会话信息
            conversation = conversation_service.get_conversation(session_id)
            if not conversation:
                return {'success': False, 'error': 'Conversation not found'}
            
            # 获取所有消息
            messages = message_service.get_session_messages(session_id)
            
            # 获取所有智能体输出
            agent_outputs = agent_output_service.get_session_agent_outputs(session_id)
            
            return {
                'success': True,
                'conversation': conversation.to_dict() if hasattr(conversation, 'to_dict') else None,
                'messages': [msg.to_dict() if hasattr(msg, 'to_dict') else None for msg in messages],
                'agent_outputs': [output.to_dict() if hasattr(output, 'to_dict') else None for output in agent_outputs]
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


# 全局单例
integration_service = IntegrationService()

