from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Conversation(Base):
    """
    会话模型 - 记录用户与客服系统的完整对话会话
    """
    __tablename__ = "conversations"

    # 会话标识
    session_id = Column(String(64), unique=True, nullable=False, index=True, comment='会话唯一标识')
    user_id = Column(String(64), ForeignKey('users.user_id'), nullable=False, index=True, comment='用户ID')
    
    # 会话基本信息
    title = Column(String(256), nullable=True, comment='会话标题（自动生成或用户设置）')
    first_question = Column(Text, nullable=False, comment='用户的第一个问题')
    last_message = Column(Text, nullable=True, comment='最后一条消息内容')
    
    # 会话状态
    status = Column(String(32), default='active', index=True, comment='会话状态: active, closed, archived, timeout')
    is_resolved = Column(Boolean, default=False, comment='问题是否已解决')
    
    # 会话统计
    message_count = Column(Integer, default=0, comment='消息总数')
    user_message_count = Column(Integer, default=0, comment='用户消息数')
    agent_message_count = Column(Integer, default=0, comment='智能体消息数')
    agent_switches = Column(Integer, default=0, comment='智能体切换次数')
    
    # 会话分类和标签
    category = Column(String(64), nullable=True, index=True, comment='会话分类: product, order, after_sales, promotion, general')
    primary_agent = Column(String(64), nullable=True, comment='主要处理的智能体')
    tags = Column(Text, nullable=True, comment='会话标签(JSON数组)')
    
    # 会话质量指标
    avg_response_time = Column(Float, default=0.0, comment='平均响应时间(秒)')
    total_duration = Column(Float, default=0.0, comment='会话总时长(秒)')
    
    # 满意度评分
    satisfaction_score = Column(Integer, nullable=True, comment='用户满意度评分(1-5)')
    feedback = Column(Text, nullable=True, comment='用户反馈')
    feedback_time = Column(DateTime(timezone=True), nullable=True, comment='反馈时间')
    
    # Token统计
    total_tokens = Column(Integer, default=0, comment='总Token使用量')
    total_cost = Column(Float, default=0.0, comment='总成本')
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), nullable=True, comment='会话开始时间')
    ended_at = Column(DateTime(timezone=True), nullable=True, comment='会话结束时间')
    last_activity_at = Column(DateTime(timezone=True), nullable=True, comment='最后活跃时间')
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    agent_outputs = relationship("AgentOutput", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', user_id='{self.user_id}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'status': self.status,
            'is_resolved': self.is_resolved,
            'message_count': self.message_count,
            'category': self.category,
            'primary_agent': self.primary_agent,
            'satisfaction_score': self.satisfaction_score,
            'total_duration': self.total_duration,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'created_time': self.created_time.isoformat() if self.created_time else None
        }
