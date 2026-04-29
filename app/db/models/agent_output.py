from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class AgentOutput(Base):
    """
    智能体输出记录模型 - 详细记录每个智能体的处理过程和输出信息
    """
    __tablename__ = "agent_outputs"

    # 关联信息
    session_id = Column(String(64), ForeignKey('conversations.session_id'), nullable=False, index=True, comment='会话ID')
    message_id = Column(String(36), ForeignKey('messages.id'), nullable=True, index=True, comment='关联的消息ID')
    user_id = Column(String(64), nullable=False, index=True, comment='用户ID')
    
    # 智能体信息
    agent_type = Column(String(64), nullable=False, index=True, comment='智能体类型: router, order_agent, product_agent等')
    agent_name = Column(String(64), nullable=False, comment='智能体名称')
    agent_version = Column(String(32), nullable=True, comment='智能体版本')
    
    # 输入信息
    input_text = Column(Text, nullable=False, comment='输入文本')
    input_tokens = Column(Integer, nullable=True, comment='输入Token数')
    
    # 输出信息
    output_text = Column(Text, nullable=False, comment='输出文本/响应内容')
    output_tokens = Column(Integer, nullable=True, comment='输出Token数')
    
    # 路由专属字段（仅router_agent使用）
    target_agent = Column(String(64), nullable=True, comment='路由目标智能体')
    confidence = Column(Float, nullable=True, comment='路由置信度(0-1)')
    user_intent = Column(String(256), nullable=True, comment='识别的用户意图')
    
    # 工具调用信息
    tools_called = Column(JSON, nullable=True, comment='调用的工具列表: [{tool_name, tool_args, tool_result}]')
    tool_count = Column(Integer, default=0, comment='调用工具的数量')
    
    # 记忆上下文
    memory_context = Column(Text, nullable=True, comment='使用的记忆上下文')
    memory_used = Column(Boolean, default=False, comment='是否使用了记忆')
    
    # 性能指标
    processing_time = Column(Float, nullable=False, comment='处理时间(秒)')
    latency = Column(Float, nullable=True, comment='延迟时间(秒)')
    
    # Token和成本
    total_tokens = Column(Integer, nullable=True, comment='总Token数')
    cost = Column(Float, nullable=True, comment='本次调用的成本')
    
    # 执行状态
    status = Column(String(32), default='success', index=True, comment='执行状态: success, failed, timeout, partial')
    error_message = Column(Text, nullable=True, comment='错误信息（如果失败）')
    
    # 质量评估
    quality_score = Column(Float, nullable=True, comment='输出质量评分(0-1)')
    is_helpful = Column(Boolean, nullable=True, comment='是否有帮助')
    
    # 元数据
    extra_data = Column(JSON, nullable=True, comment='额外的元数据信息')
    
    # 执行序号
    execution_order = Column(Integer, nullable=False, comment='在会话中的执行顺序')
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), nullable=False, comment='开始处理时间')
    completed_at = Column(DateTime(timezone=True), nullable=True, comment='完成处理时间')
    
    # 关系
    conversation = relationship("Conversation", back_populates="agent_outputs")
    
    def __repr__(self):
        return f"<AgentOutput(agent_type='{self.agent_type}', status='{self.status}', execution_order={self.execution_order})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_id': self.message_id,
            'agent_type': self.agent_type,
            'agent_name': self.agent_name,
            'input_text': self.input_text[:200] + '...' if len(self.input_text) > 200 else self.input_text,
            'output_text': self.output_text[:200] + '...' if len(self.output_text) > 200 else self.output_text,
            'target_agent': self.target_agent,
            'confidence': self.confidence,
            'user_intent': self.user_intent,
            'processing_time': self.processing_time,
            'total_tokens': self.total_tokens,
            'cost': self.cost,
            'status': self.status,
            'tools_called': self.tools_called,
            'execution_order': self.execution_order,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class AgentPerformance(Base):
    """
    智能体性能指标模型 - 记录智能体的实时性能数据
    """
    __tablename__ = "agent_performance"

    # 智能体信息
    agent_type = Column(String(64), nullable=False, index=True, comment='智能体类型')
    agent_name = Column(String(64), nullable=False, comment='智能体名称')
    
    # 时间窗口
    time_window = Column(String(32), nullable=False, comment='时间窗口: hourly, daily, weekly, monthly')
    window_start = Column(DateTime(timezone=True), nullable=False, index=True, comment='窗口开始时间')
    window_end = Column(DateTime(timezone=True), nullable=False, comment='窗口结束时间')
    
    # 使用统计
    total_calls = Column(Integer, default=0, comment='总调用次数')
    successful_calls = Column(Integer, default=0, comment='成功调用次数')
    failed_calls = Column(Integer, default=0, comment='失败调用次数')
    
    # 性能统计
    avg_processing_time = Column(Float, default=0.0, comment='平均处理时间(秒)')
    min_processing_time = Column(Float, nullable=True, comment='最小处理时间(秒)')
    max_processing_time = Column(Float, nullable=True, comment='最大处理时间(秒)')
    p95_processing_time = Column(Float, nullable=True, comment='P95处理时间(秒)')
    
    # Token统计
    total_tokens = Column(Integer, default=0, comment='总Token使用量')
    avg_tokens_per_call = Column(Float, default=0.0, comment='每次调用平均Token数')
    
    # 成本统计
    total_cost = Column(Float, default=0.0, comment='总成本')
    avg_cost_per_call = Column(Float, default=0.0, comment='每次调用平均成本')
    
    # 质量统计
    avg_quality_score = Column(Float, nullable=True, comment='平均质量评分')
    helpful_rate = Column(Float, nullable=True, comment='有帮助率')
    
    # 工具使用统计
    tools_usage = Column(JSON, nullable=True, comment='工具使用统计: {tool_name: count}')
    
    # 详细数据
    detailed_metrics = Column(JSON, nullable=True, comment='详细性能指标')
    
    def __repr__(self):
        return f"<AgentPerformance(agent_type='{self.agent_type}', window='{self.time_window}', calls={self.total_calls})>"

