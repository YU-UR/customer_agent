from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Message(Base):
    """
    消息模型 - 记录会话中的每条消息（用户和助手）
    """
    __tablename__ = "messages"

    # 关联信息
    session_id = Column(String(64), ForeignKey('conversations.session_id'), nullable=False, index=True, comment='会话ID')
    user_id = Column(String(64), ForeignKey('users.user_id'), nullable=False, index=True, comment='用户ID')
    
    # 消息基本信息
    role = Column(String(32), nullable=False, index=True, comment='消息角色: user, assistant, system')
    content = Column(Text, nullable=False, comment='消息内容')
    message_type = Column(String(32), default='text', comment='消息类型: text, image, file, system, error')
    
    # 消息序号
    sequence = Column(Integer, nullable=False, comment='消息在会话中的序号')
    
    # 智能体信息
    agent_type = Column(String(64), nullable=True, index=True, comment='智能体类型: order_agent, product_agent等')
    agent_name = Column(String(64), nullable=True, comment='智能体名称')
    
    # 路由信息
    router_confidence = Column(Float, nullable=True, comment='路由置信度')
    user_intent = Column(String(256), nullable=True, comment='用户意图')
    
    # 消息处理信息
    processing_time = Column(Float, nullable=True, comment='消息处理时间(秒)')
    response_time = Column(Float, nullable=True, comment='响应时间(秒)')
    
    # Token使用情况
    token_usage = Column(JSON, nullable=True, comment='Token使用情况: {input: xxx, output: xxx, total: xxx}')
    cost = Column(Float, nullable=True, comment='本条消息的成本')
    
    # 消息状态
    is_edited = Column(Boolean, default=False, comment='是否已编辑')
    is_deleted = Column(Boolean, default=False, comment='是否已删除')
    is_error = Column(Boolean, default=False, comment='是否是错误消息')
    
    # 消息元数据
    extra_data = Column(JSON, nullable=True, comment='消息元数据: {tools_used: [], memory_context: {}}')
    
    # 消息评分
    rating = Column(Integer, nullable=True, comment='消息评分(1-5)')
    rating_reason = Column(Text, nullable=True, comment='评分原因')
    
    # 父消息ID（用于编辑历史）
    parent_message_id = Column(String(36), nullable=True, comment='父消息ID')
    
    # 时间戳
    sent_at = Column(DateTime(timezone=True), nullable=True, comment='消息发送时间')
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
    feedbacks = relationship("MessageFeedback", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(session_id='{self.session_id}', role='{self.role}', agent_type='{self.agent_type}', seq={self.sequence})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'message_type': self.message_type,
            'sequence': self.sequence,
            'agent_type': self.agent_type,
            'agent_name': self.agent_name,
            'processing_time': self.processing_time,
            'rating': self.rating,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }


class MessageFeedback(Base):
    """
    消息反馈模型 - 记录用户对消息的反馈
    """
    __tablename__ = "message_feedbacks"

    # 关联信息
    message_id = Column(String(36), ForeignKey('messages.id'), nullable=False, index=True, comment='消息ID')
    user_id = Column(String(64), ForeignKey('users.user_id'), nullable=False, index=True, comment='用户ID')
    session_id = Column(String(64), nullable=True, comment='会话ID')
    
    # 反馈类型
    feedback_type = Column(String(32), nullable=False, index=True, comment='反馈类型: like, dislike, helpful, not_helpful, report')
    
    # 反馈内容
    feedback_text = Column(Text, nullable=True, comment='反馈文本')
    
    # 反馈标签
    tags = Column(JSON, nullable=True, comment='反馈标签: ["不准确", "不相关", "有帮助"]')
    
    # 反馈详情
    issue_category = Column(String(64), nullable=True, comment='问题分类')
    severity = Column(String(32), nullable=True, comment='严重程度: low, medium, high')
    
    # 处理状态
    is_resolved = Column(Boolean, default=False, comment='是否已处理')
    resolved_by = Column(String(64), nullable=True, comment='处理人')
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment='处理时间')
    
    # 关系
    message = relationship("Message", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<MessageFeedback(message_id='{self.message_id}', feedback_type='{self.feedback_type}')>"
