"""
用户服务 - 处理用户相关的业务逻辑
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_or_get_user(user_id: str, **kwargs) -> User:
        """创建或获取用户"""
        with get_db() as db:
            # 尝试获取现有用户
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if user:
                # 更新最后活跃时间
                user.last_active_time = datetime.now()
                db.commit()
                db.refresh(user)
                logger.info(f"User {user_id} already exists, updated last_active_time")
                return user
            
            # 创建新用户
            user = User(
                user_id=user_id,
                username=kwargs.get('username'),
                email=kwargs.get('email'),
                phone=kwargs.get('phone'),
                nickname=kwargs.get('nickname'),
                avatar=kwargs.get('avatar'),
                first_visit_time=datetime.now(),
                last_active_time=datetime.now()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created new user: {user_id}")
            return user
    
    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """获取用户信息"""
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            return user
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> Optional[User]:
        """更新用户信息"""
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            # 更新允许的字段
            updatable_fields = [
                'username', 'email', 'phone', 'nickname', 'avatar',
                'is_vip', 'user_level', 'points', 'preferences'
            ]
            
            for field in updatable_fields:
                if field in kwargs and kwargs[field] is not None:
                    setattr(user, field, kwargs[field])
            
            user.last_active_time = datetime.now()
            db.commit()
            db.refresh(user)
            
            logger.info(f"Updated user: {user_id}")
            return user
    
    @staticmethod
    def update_user_stats(user_id: str, increment_conversations: int = 0, 
                         increment_messages: int = 0) -> Optional[User]:
        """更新用户统计信息"""
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                return None
            
            user.total_conversations += increment_conversations
            user.total_messages += increment_messages
            user.last_active_time = datetime.now()
            
            db.commit()
            db.refresh(user)
            
            return user
    
    @staticmethod
    def update_user_satisfaction(user_id: str, new_rating: int) -> Optional[User]:
        """更新用户平均满意度"""
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                return None
            
            # 计算新的平均满意度（简单移动平均）
            total_ratings = user.total_conversations
            if total_ratings > 0:
                current_total = user.avg_satisfaction * total_ratings
                new_total = current_total + new_rating
                user.avg_satisfaction = int(new_total / (total_ratings + 1))
            else:
                user.avg_satisfaction = new_rating
            
            db.commit()
            db.refresh(user)
            
            return user
    
    @staticmethod
    def get_user_dict(user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息（字典格式）"""
        user = UserService.get_user(user_id)
        if user:
            return user.to_dict()
        return None


# 全局单例
user_service = UserService()

