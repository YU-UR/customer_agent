from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class AgentUsageStats(Base):
    """
    智能体使用统计模型 - 按日期统计智能体的使用情况
    """
    __tablename__ = "agent_usage_stats"

    # 智能体信息
    agent_id = Column(String(64), nullable=False, index=True, comment='智能体ID')
    agent_name = Column(String(64), nullable=False, comment='智能体名称')
    agent_type = Column(String(64), nullable=False, index=True, comment='智能体类型')
    
    # 统计时间范围
    stats_date = Column(DateTime(timezone=True), nullable=False, index=True, comment='统计日期')
    stats_period = Column(String(32), default='daily', comment='统计周期: hourly, daily, weekly, monthly')
    
    # 使用统计
    total_conversations = Column(Integer, default=0, comment='总会话数')
    total_messages = Column(Integer, default=0, comment='总消息数')
    unique_users = Column(Integer, default=0, comment='独立用户数')
    
    # 时间统计
    total_processing_time = Column(Float, default=0.0, comment='总处理时间(秒)')
    avg_processing_time = Column(Float, default=0.0, comment='平均处理时间(秒)')
    max_processing_time = Column(Float, default=0.0, comment='最大处理时间(秒)')
    
    # 成功率统计
    successful_resolutions = Column(Integer, default=0, comment='成功解决问题数')
    failed_resolutions = Column(Integer, default=0, comment='失败处理数')
    success_rate = Column(Float, default=0.0, comment='成功率')
    
    # 满意度统计
    user_satisfaction_avg = Column(Float, default=0.0, comment='用户满意度平均分')
    total_ratings = Column(Integer, default=0, comment='总评分数')
    rating_distribution = Column(JSON, nullable=True, comment='评分分布: {1: count, 2: count, ...}')
    
    # Token使用统计
    total_tokens_used = Column(Integer, default=0, comment='总Token使用量')
    avg_tokens_per_message = Column(Float, default=0.0, comment='每条消息平均Token数')
    
    # 成本统计
    total_cost = Column(Float, default=0.0, comment='总成本')
    avg_cost_per_conversation = Column(Float, default=0.0, comment='每次会话平均成本')
    
    # 工具使用统计
    tools_used = Column(JSON, nullable=True, comment='工具使用统计: {tool_name: count}')
    
    # 详细统计数据
    detailed_stats = Column(JSON, nullable=True, comment='详细统计数据')
    
    # 趋势分析
    compared_to_previous = Column(JSON, nullable=True, comment='与上一周期对比: {metric: change_percentage}')
    
    def __repr__(self):
        return f"<AgentUsageStats(agent_type='{self.agent_type}', date='{self.stats_date}', conversations={self.total_conversations})>"


class SystemMetrics(Base):
    """
    系统指标模型 - 记录整体系统的性能和使用指标
    """
    __tablename__ = "system_metrics"

    # 指标信息
    metric_name = Column(String(128), nullable=False, index=True, comment='指标名称')
    metric_value = Column(Float, nullable=False, comment='指标值')
    metric_unit = Column(String(32), nullable=True, comment='指标单位: seconds, count, percentage, bytes')
    
    # 指标分类
    category = Column(String(64), nullable=False, index=True, comment='指标分类: performance, usage, quality, cost, availability')
    subcategory = Column(String(64), nullable=True, comment='子分类')
    
    # 指标元数据
    extra_data = Column(JSON, nullable=True, comment='指标元数据')
    tags = Column(JSON, nullable=True, comment='标签')
    
    # 时间维度
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True, comment='记录时间')
    time_window = Column(String(32), nullable=True, comment='时间窗口: realtime, hourly, daily')
    
    # 阈值信息
    threshold_value = Column(Float, nullable=True, comment='阈值')
    is_alert = Column(Boolean, default=False, comment='是否触发告警')
    alert_level = Column(String(32), nullable=True, comment='告警级别: info, warning, error, critical')
    
    def __repr__(self):
        return f"<SystemMetrics(metric_name='{self.metric_name}', value={self.metric_value}, category='{self.category}')>"


class KnowledgeBase(Base):
    """
    知识库模型 - 存储系统使用的知识条目
    """
    __tablename__ = "knowledge_base"

    # 知识基本信息
    title = Column(String(256), nullable=False, index=True, comment='知识条目标题')
    content = Column(Text, nullable=False, comment='知识内容')
    summary = Column(String(512), nullable=True, comment='内容摘要')
    
    # 分类和标签
    category = Column(String(64), nullable=False, index=True, comment='知识分类: product, order, policy, faq等')
    subcategory = Column(String(64), nullable=True, comment='子分类')
    tags = Column(JSON, nullable=True, comment='标签列表')
    keywords = Column(JSON, nullable=True, comment='关键词列表')
    
    # 知识状态
    is_active = Column(Boolean, default=True, index=True, comment='是否激活')
    is_verified = Column(Boolean, default=False, comment='是否已验证')
    is_public = Column(Boolean, default=True, comment='是否公开')
    
    # 优先级和质量
    priority = Column(Integer, default=0, comment='优先级(数字越大优先级越高)')
    quality_score = Column(Float, default=0.0, comment='质量评分(0-1)')
    relevance_score = Column(Float, default=0.0, comment='相关性评分(0-1)')
    
    # 使用统计
    view_count = Column(Integer, default=0, comment='查看次数')
    use_count = Column(Integer, default=0, comment='使用次数')
    helpful_count = Column(Integer, default=0, comment='有帮助次数')
    not_helpful_count = Column(Integer, default=0, comment='无帮助次数')
    
    # 适用范围
    applicable_agents = Column(JSON, nullable=True, comment='适用的智能体列表')
    
    # 版本控制
    version = Column(String(32), nullable=True, comment='版本号')
    previous_version_id = Column(String(36), nullable=True, comment='上一版本ID')
    
    # 创建和维护信息
    created_by = Column(String(64), nullable=True, comment='创建者')
    updated_by = Column(String(64), nullable=True, comment='更新者')
    reviewed_by = Column(String(64), nullable=True, comment='审核者')
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment='审核时间')
    
    # 过期信息
    expires_at = Column(DateTime(timezone=True), nullable=True, comment='过期时间')
    is_expired = Column(Boolean, default=False, comment='是否已过期')
    
    # 额外元数据
    extra_data = Column(JSON, nullable=True, comment='额外元数据')
    
    def __repr__(self):
        return f"<KnowledgeBase(title='{self.title}', category='{self.category}', is_active={self.is_active})>"


class ErrorLog(Base):
    """
    错误日志模型 - 记录系统运行中的错误
    """
    __tablename__ = "error_logs"

    # 错误基本信息
    error_type = Column(String(128), nullable=False, index=True, comment='错误类型')
    error_message = Column(Text, nullable=False, comment='错误消息')
    error_code = Column(String(64), nullable=True, comment='错误代码')
    
    # 错误级别
    severity = Column(String(32), nullable=False, index=True, comment='严重程度: debug, info, warning, error, critical')
    
    # 错误来源
    source = Column(String(128), nullable=True, comment='错误来源: agent_type, api_endpoint等')
    module = Column(String(128), nullable=True, comment='模块名称')
    function = Column(String(128), nullable=True, comment='函数名称')
    
    # 上下文信息
    session_id = Column(String(64), nullable=True, index=True, comment='会话ID')
    user_id = Column(String(64), nullable=True, index=True, comment='用户ID')
    
    # 错误详情
    stack_trace = Column(Text, nullable=True, comment='堆栈跟踪')
    request_data = Column(JSON, nullable=True, comment='请求数据')
    response_data = Column(JSON, nullable=True, comment='响应数据')
    
    # 处理状态
    is_resolved = Column(Boolean, default=False, comment='是否已解决')
    resolved_by = Column(String(64), nullable=True, comment='解决人')
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment='解决时间')
    resolution_notes = Column(Text, nullable=True, comment='解决说明')
    
    # 额外信息
    extra_data = Column(JSON, nullable=True, comment='额外元数据')
    
    def __repr__(self):
        return f"<ErrorLog(error_type='{self.error_type}', severity='{self.severity}', resolved={self.is_resolved})>"
