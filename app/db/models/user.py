from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    用户模型 - 记录系统用户信息
    """
    __tablename__ = "users"

    # 用户唯一标识
    user_id = Column(String(64), unique=True, nullable=False, index=True, comment='用户唯一标识')
    
    # 基本信息
    username = Column(String(64), nullable=True, index=True, comment='用户名')
    email = Column(String(128), nullable=True, unique=True, index=True, comment='邮箱')
    phone = Column(String(32), nullable=True, unique=True, index=True, comment='手机号')
    avatar = Column(String(512), nullable=True, comment='头像URL')
    nickname = Column(String(64), nullable=True, comment='昵称')
    # 认证信息
    password_hash = Column(String(256), nullable=True, comment='密码哈希')
    
    # 用户状态
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_vip = Column(Boolean, default=False, comment='是否VIP用户')
    is_blocked = Column(Boolean, default=False, comment='是否被封禁')
    
    # 用户等级和积分
    user_level = Column(Integer, default=1, comment='用户等级')
    points = Column(Integer, default=0, comment='用户积分')
    
    # 用户偏好设置（JSON格式）
    preferences = Column(Text, nullable=True, comment='用户偏好设置(JSON格式)')
    
    # 统计信息
    total_conversations = Column(Integer, default=0, comment='总会话数')
    total_messages = Column(Integer, default=0, comment='总消息数')
    avg_satisfaction = Column(Integer, default=0, comment='平均满意度评分')
    
    # 时间戳
    last_active_time = Column(DateTime(timezone=True), nullable=True, comment='最后活跃时间')
    first_visit_time = Column(DateTime(timezone=True), nullable=True, comment='首次访问时间')
    
    # 关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', username='{self.username}', is_active={self.is_active})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'nickname': self.nickname,
            'is_vip': self.is_vip,
            'user_level': self.user_level,
            'points': self.points,
            'total_conversations': self.total_conversations,
            'total_messages': self.total_messages,
            'avg_satisfaction': self.avg_satisfaction,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'last_active_time': self.last_active_time.isoformat() if self.last_active_time else None
        }
