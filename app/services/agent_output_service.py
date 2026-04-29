"""
智能体输出服务 - 记录智能体的执行过程和输出
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.agent_output import AgentOutput, AgentPerformance
from app.db.session import get_db
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class AgentOutputService:
    """智能体输出服务类"""
    
    @staticmethod
    def create_agent_output(session_id: str, user_id: str, agent_type: str,
                           agent_name: str, input_text: str, output_text: str,
                           execution_order: int, processing_time: float,
                           **kwargs) -> AgentOutput:
        """创建智能体输出记录"""
        with get_db() as db:
            output = AgentOutput(
                session_id=session_id,
                message_id=kwargs.get('message_id'),
                user_id=user_id,
                agent_type=agent_type,
                agent_name=agent_name,
                agent_version=kwargs.get('agent_version'),
                input_text=input_text,
                input_tokens=kwargs.get('input_tokens'),
                output_text=output_text,
                output_tokens=kwargs.get('output_tokens'),
                # 路由专属字段
                target_agent=kwargs.get('target_agent'),
                confidence=kwargs.get('confidence'),
                user_intent=kwargs.get('user_intent'),
                # 工具调用
                tools_called=kwargs.get('tools_called'),
                tool_count=len(kwargs.get('tools_called', [])),
                # 记忆
                memory_context=kwargs.get('memory_context'),
                memory_used=kwargs.get('memory_used', False),
                # 性能
                processing_time=processing_time,
                latency=kwargs.get('latency'),
                total_tokens=kwargs.get('total_tokens'),
                cost=kwargs.get('cost'),
                # 状态
                status=kwargs.get('status', 'success'),
                error_message=kwargs.get('error_message'),
                # 质量
                quality_score=kwargs.get('quality_score'),
                is_helpful=kwargs.get('is_helpful'),
                extra_data=kwargs.get('extra_data'),
                execution_order=execution_order,
                started_at=kwargs.get('started_at', datetime.now()),
                completed_at=datetime.now()
            )
            
            db.add(output)
            db.commit()
            db.refresh(output)
            
            logger.info(f"Created agent output: {output.id} for agent: {agent_type}")
            return output
    
    @staticmethod
    def get_agent_output(output_id: str) -> Optional[AgentOutput]:
        """获取智能体输出记录"""
        with get_db() as db:
            output = db.query(AgentOutput).filter(AgentOutput.id == output_id).first()
            return output
    
    @staticmethod
    def get_session_agent_outputs(session_id: str) -> List[AgentOutput]:
        """获取会话的所有智能体输出"""
        with get_db() as db:
            outputs = db.query(AgentOutput).filter(
                AgentOutput.session_id == session_id
            ).order_by(AgentOutput.execution_order).all()
            return outputs
    
    @staticmethod
    def get_agent_outputs_by_type(session_id: str, agent_type: str) -> List[AgentOutput]:
        """获取指定类型的智能体输出"""
        with get_db() as db:
            outputs = db.query(AgentOutput).filter(
                AgentOutput.session_id == session_id,
                AgentOutput.agent_type == agent_type
            ).order_by(AgentOutput.execution_order).all()
            return outputs
    
    @staticmethod
    def get_next_execution_order(session_id: str) -> int:
        """获取下一个执行序号"""
        with get_db() as db:
            last_output = db.query(AgentOutput).filter(
                AgentOutput.session_id == session_id
            ).order_by(desc(AgentOutput.execution_order)).first()
            
            if last_output:
                return last_output.execution_order + 1
            return 1
    
    @staticmethod
    def get_router_decisions(session_id: str) -> List[AgentOutput]:
        """获取路由决策记录"""
        with get_db() as db:
            outputs = db.query(AgentOutput).filter(
                AgentOutput.session_id == session_id,
                AgentOutput.agent_type == 'router_agent'
            ).order_by(AgentOutput.execution_order).all()
            return outputs
    
    @staticmethod
    def get_agent_statistics(agent_type: str, days: int = 7) -> Dict[str, Any]:
        """获取智能体统计数据"""
        with get_db() as db:
            from sqlalchemy import func
            from datetime import timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            stats = db.query(
                func.count(AgentOutput.id).label('total_calls'),
                func.avg(AgentOutput.processing_time).label('avg_processing_time'),
                func.sum(AgentOutput.total_tokens).label('total_tokens'),
                func.sum(AgentOutput.cost).label('total_cost'),
                func.avg(AgentOutput.confidence).label('avg_confidence')
            ).filter(
                AgentOutput.agent_type == agent_type,
                AgentOutput.created_time >= start_date
            ).first()
            
            return {
                'agent_type': agent_type,
                'period_days': days,
                'total_calls': stats.total_calls or 0,
                'avg_processing_time': float(stats.avg_processing_time or 0),
                'total_tokens': int(stats.total_tokens or 0),
                'total_cost': float(stats.total_cost or 0),
                'avg_confidence': float(stats.avg_confidence or 0) if stats.avg_confidence else None
            }
    
    @staticmethod
    def update_quality_score(output_id: str, quality_score: float, 
                            is_helpful: Optional[bool] = None) -> Optional[AgentOutput]:
        """更新输出质量评分"""
        with get_db() as db:
            output = db.query(AgentOutput).filter(AgentOutput.id == output_id).first()
            
            if not output:
                return None
            
            output.quality_score = quality_score
            if is_helpful is not None:
                output.is_helpful = is_helpful
            
            db.commit()
            db.refresh(output)
            
            return output


# 全局单例
agent_output_service = AgentOutputService()

