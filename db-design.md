# 智能电商客服系统 - 数据库设计文档

## 📋 概述

本文档详细说明了智能电商客服系统的数据库结构设计，包括10张核心数据表，涵盖用户管理、会话记录、消息存储、智能体输出追踪、性能统计等功能。

---

## 🗄️ 数据表总览

| 序号 | 表名 | 说明 | 记录数量预估 |
|------|------|------|--------------|
| 1 | `users` | 用户表 | 10万+ |
| 2 | `conversations` | 会话表 | 100万+ |
| 3 | `messages` | 消息记录表 | 1000万+ |
| 4 | `message_feedbacks` | 消息反馈表 | 10万+ |
| 5 | `agent_outputs` | 智能体输出记录表 | 500万+ |
| 6 | `agent_performance` | 智能体性能表 | 1万+ |
| 7 | `agent_usage_stats` | 智能体使用统计表 | 1万+ |
| 8 | `system_metrics` | 系统指标表 | 100万+ |
| 9 | `knowledge_base` | 知识库表 | 1万+ |
| 10 | `error_logs` | 错误日志表 | 10万+ |

---

## 📊 详细表结构

### 1. users - 用户表

**用途：** 存储系统用户的基本信息和统计数据

**主要字段：**

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY COMMENT 'UUID主键',
    user_id VARCHAR(64) UNIQUE NOT NULL COMMENT '用户唯一标识',
    username VARCHAR(64) COMMENT '用户名',
    email VARCHAR(128) UNIQUE COMMENT '邮箱',
    phone VARCHAR(32) UNIQUE COMMENT '手机号',
    avatar VARCHAR(512) COMMENT '头像URL',
    nickname VARCHAR(64) COMMENT '昵称',
    
    -- 状态字段
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_vip BOOLEAN DEFAULT FALSE COMMENT '是否VIP',
    is_blocked BOOLEAN DEFAULT FALSE COMMENT '是否封禁',
    
    -- 等级积分
    user_level INT DEFAULT 1 COMMENT '用户等级',
    points INT DEFAULT 0 COMMENT '用户积分',
    
    -- 统计信息
    total_conversations INT DEFAULT 0 COMMENT '总会话数',
    total_messages INT DEFAULT 0 COMMENT '总消息数',
    avg_satisfaction INT DEFAULT 0 COMMENT '平均满意度',
    
    -- 时间戳
    created_time DATETIME COMMENT '创建时间',
    updated_time DATETIME COMMENT '更新时间',
    last_active_time DATETIME COMMENT '最后活跃时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_email (email),
    INDEX idx_phone (phone)
);
```

**关系：**
- 一个用户可以有多个会话（1:N → conversations）
- 一个用户可以发送多条消息（1:N → messages）

---

### 2. conversations - 会话表

**用途：** 记录用户与系统的完整对话会话

**主要字段：**

```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL COMMENT '会话唯一标识',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    
    -- 会话信息
    title VARCHAR(256) COMMENT '会话标题',
    first_question TEXT NOT NULL COMMENT '首个问题',
    last_message TEXT COMMENT '最后一条消息',
    
    -- 状态
    status VARCHAR(32) DEFAULT 'active' COMMENT '状态: active, closed, archived, timeout',
    is_resolved BOOLEAN DEFAULT FALSE COMMENT '是否已解决',
    
    -- 统计
    message_count INT DEFAULT 0 COMMENT '消息总数',
    user_message_count INT DEFAULT 0 COMMENT '用户消息数',
    agent_message_count INT DEFAULT 0 COMMENT '智能体消息数',
    agent_switches INT DEFAULT 0 COMMENT '智能体切换次数',
    
    -- 分类
    category VARCHAR(64) COMMENT '分类: product, order, after_sales等',
    primary_agent VARCHAR(64) COMMENT '主要处理智能体',
    tags TEXT COMMENT '标签JSON',
    
    -- 质量指标
    avg_response_time FLOAT DEFAULT 0.0 COMMENT '平均响应时间(秒)',
    total_duration FLOAT DEFAULT 0.0 COMMENT '总时长(秒)',
    
    -- 满意度
    satisfaction_score INT COMMENT '满意度评分(1-5)',
    feedback TEXT COMMENT '用户反馈',
    
    -- Token统计
    total_tokens INT DEFAULT 0 COMMENT '总Token数',
    total_cost FLOAT DEFAULT 0.0 COMMENT '总成本',
    
    -- 时间戳
    created_time DATETIME,
    updated_time DATETIME,
    started_at DATETIME COMMENT '开始时间',
    ended_at DATETIME COMMENT '结束时间',
    last_activity_at DATETIME COMMENT '最后活跃时间',
    
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_category (category),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**关系：**
- 属于一个用户（N:1 → users）
- 包含多条消息（1:N → messages）
- 包含多条智能体输出记录（1:N → agent_outputs）

---

### 3. messages - 消息记录表

**用途：** 存储会话中的每条消息（用户消息和助手回复）

**主要字段：**

```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    
    -- 消息基本信息
    role VARCHAR(32) NOT NULL COMMENT '角色: user, assistant, system',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(32) DEFAULT 'text' COMMENT '类型: text, image, file, error',
    sequence INT NOT NULL COMMENT '消息序号',
    
    -- 智能体信息
    agent_type VARCHAR(64) COMMENT '智能体类型',
    agent_name VARCHAR(64) COMMENT '智能体名称',
    
    -- 路由信息
    router_confidence FLOAT COMMENT '路由置信度',
    user_intent VARCHAR(256) COMMENT '用户意图',
    
    -- 性能信息
    processing_time FLOAT COMMENT '处理时间(秒)',
    response_time FLOAT COMMENT '响应时间(秒)',
    
    -- Token统计
    token_usage JSON COMMENT 'Token使用: {input, output, total}',
    cost FLOAT COMMENT '成本',
    
    -- 状态
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_error BOOLEAN DEFAULT FALSE,
    
    -- 元数据
    metadata JSON COMMENT '元数据',
    
    -- 评分
    rating INT COMMENT '评分(1-5)',
    rating_reason TEXT COMMENT '评分原因',
    
    -- 父消息（编辑历史）
    parent_message_id VARCHAR(36) COMMENT '父消息ID',
    
    -- 时间戳
    created_time DATETIME,
    updated_time DATETIME,
    sent_at DATETIME COMMENT '发送时间',
    
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role (role),
    INDEX idx_agent_type (agent_type),
    FOREIGN KEY (session_id) REFERENCES conversations(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**关键特性：**
- `sequence` 字段确保消息顺序
- `agent_type` 记录处理该消息的智能体
- `token_usage` 存储详细的Token使用情况
- `metadata` 可以存储工具调用、记忆上下文等额外信息

---

### 4. message_feedbacks - 消息反馈表

**用途：** 记录用户对消息的反馈（点赞、点踩、举报等）

**主要字段：**

```sql
CREATE TABLE message_feedbacks (
    id VARCHAR(36) PRIMARY KEY,
    message_id VARCHAR(36) NOT NULL COMMENT '消息ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    session_id VARCHAR(64) COMMENT '会话ID',
    
    -- 反馈类型
    feedback_type VARCHAR(32) NOT NULL COMMENT '类型: like, dislike, helpful, report',
    
    -- 反馈内容
    feedback_text TEXT COMMENT '反馈文本',
    tags JSON COMMENT '反馈标签',
    
    -- 问题分类
    issue_category VARCHAR(64) COMMENT '问题分类',
    severity VARCHAR(32) COMMENT '严重程度: low, medium, high',
    
    -- 处理状态
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(64) COMMENT '处理人',
    resolved_at DATETIME COMMENT '处理时间',
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id),
    INDEX idx_feedback_type (feedback_type),
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

---

### 5. agent_outputs - 智能体输出记录表 ⭐

**用途：** 详细记录每个智能体的输入、输出、处理过程和性能数据

**主要字段：**

```sql
CREATE TABLE agent_outputs (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    message_id VARCHAR(36) COMMENT '关联消息ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    
    -- 智能体信息
    agent_type VARCHAR(64) NOT NULL COMMENT '智能体类型',
    agent_name VARCHAR(64) NOT NULL COMMENT '智能体名称',
    agent_version VARCHAR(32) COMMENT '版本',
    
    -- 输入输出
    input_text TEXT NOT NULL COMMENT '输入文本',
    input_tokens INT COMMENT '输入Token数',
    output_text TEXT NOT NULL COMMENT '输出文本',
    output_tokens INT COMMENT '输出Token数',
    
    -- 路由专属字段（router_agent使用）
    target_agent VARCHAR(64) COMMENT '路由目标',
    confidence FLOAT COMMENT '置信度(0-1)',
    user_intent VARCHAR(256) COMMENT '用户意图',
    
    -- 工具调用
    tools_called JSON COMMENT '调用的工具: [{tool_name, args, result}]',
    tool_count INT DEFAULT 0 COMMENT '工具数量',
    
    -- 记忆上下文
    memory_context TEXT COMMENT '记忆上下文',
    memory_used BOOLEAN DEFAULT FALSE COMMENT '是否使用记忆',
    
    -- 性能指标
    processing_time FLOAT NOT NULL COMMENT '处理时间(秒)',
    latency FLOAT COMMENT '延迟(秒)',
    
    -- Token和成本
    total_tokens INT COMMENT '总Token数',
    cost FLOAT COMMENT '成本',
    
    -- 执行状态
    status VARCHAR(32) DEFAULT 'success' COMMENT '状态: success, failed, timeout',
    error_message TEXT COMMENT '错误信息',
    
    -- 质量评估
    quality_score FLOAT COMMENT '质量评分(0-1)',
    is_helpful BOOLEAN COMMENT '是否有帮助',
    
    -- 元数据
    metadata JSON COMMENT '额外元数据',
    
    -- 执行顺序
    execution_order INT NOT NULL COMMENT '执行顺序',
    
    -- 时间戳
    created_time DATETIME,
    updated_time DATETIME,
    started_at DATETIME NOT NULL COMMENT '开始时间',
    completed_at DATETIME COMMENT '完成时间',
    
    INDEX idx_session_id (session_id),
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id),
    INDEX idx_agent_type (agent_type),
    INDEX idx_status (status),
    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
);
```

**关键特性：**
- **完整记录智能体执行过程** - 输入、输出、工具调用、记忆使用
- **路由信息** - router_agent的路由决策（target_agent, confidence）
- **性能追踪** - 处理时间、Token使用、成本
- **执行顺序** - execution_order 字段记录智能体调用顺序
- **支持所有智能体类型** - router, order_agent, product_agent等

---

### 6. agent_performance - 智能体性能表

**用途：** 按时间窗口统计智能体的性能指标

**主要字段：**

```sql
CREATE TABLE agent_performance (
    id VARCHAR(36) PRIMARY KEY,
    agent_type VARCHAR(64) NOT NULL,
    agent_name VARCHAR(64) NOT NULL,
    
    -- 时间窗口
    time_window VARCHAR(32) NOT NULL COMMENT 'hourly, daily, weekly, monthly',
    window_start DATETIME NOT NULL,
    window_end DATETIME NOT NULL,
    
    -- 调用统计
    total_calls INT DEFAULT 0,
    successful_calls INT DEFAULT 0,
    failed_calls INT DEFAULT 0,
    
    -- 性能统计
    avg_processing_time FLOAT DEFAULT 0.0,
    min_processing_time FLOAT,
    max_processing_time FLOAT,
    p95_processing_time FLOAT COMMENT 'P95百分位',
    
    -- Token统计
    total_tokens INT DEFAULT 0,
    avg_tokens_per_call FLOAT DEFAULT 0.0,
    
    -- 成本统计
    total_cost FLOAT DEFAULT 0.0,
    avg_cost_per_call FLOAT DEFAULT 0.0,
    
    -- 质量统计
    avg_quality_score FLOAT,
    helpful_rate FLOAT,
    
    -- 工具使用
    tools_usage JSON COMMENT '{tool_name: count}',
    
    detailed_metrics JSON COMMENT '详细指标',
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_agent_type (agent_type),
    INDEX idx_window_start (window_start)
);
```

---

### 7. agent_usage_stats - 智能体使用统计表

**用途：** 按日期统计智能体的使用情况和业务指标

**主要字段：**

```sql
CREATE TABLE agent_usage_stats (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    agent_name VARCHAR(64) NOT NULL,
    agent_type VARCHAR(64) NOT NULL,
    
    -- 统计时间
    stats_date DATETIME NOT NULL,
    stats_period VARCHAR(32) DEFAULT 'daily' COMMENT 'hourly, daily, weekly',
    
    -- 使用统计
    total_conversations INT DEFAULT 0,
    total_messages INT DEFAULT 0,
    unique_users INT DEFAULT 0,
    
    -- 时间统计
    total_processing_time FLOAT DEFAULT 0.0,
    avg_processing_time FLOAT DEFAULT 0.0,
    
    -- 成功率
    successful_resolutions INT DEFAULT 0,
    failed_resolutions INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    
    -- 满意度
    user_satisfaction_avg FLOAT DEFAULT 0.0,
    total_ratings INT DEFAULT 0,
    rating_distribution JSON COMMENT '{1: count, 2: count, ...}',
    
    -- Token和成本
    total_tokens_used INT DEFAULT 0,
    total_cost FLOAT DEFAULT 0.0,
    
    -- 工具使用
    tools_used JSON COMMENT '{tool_name: count}',
    
    detailed_stats JSON,
    compared_to_previous JSON COMMENT '与上期对比',
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_agent_type (agent_type),
    INDEX idx_stats_date (stats_date)
);
```

---

### 8. system_metrics - 系统指标表

**用途：** 记录整体系统的性能和运行指标

**主要字段：**

```sql
CREATE TABLE system_metrics (
    id VARCHAR(36) PRIMARY KEY,
    metric_name VARCHAR(128) NOT NULL COMMENT '指标名称',
    metric_value FLOAT NOT NULL COMMENT '指标值',
    metric_unit VARCHAR(32) COMMENT '单位: seconds, count, percentage',
    
    -- 分类
    category VARCHAR(64) NOT NULL COMMENT 'performance, usage, quality, cost',
    subcategory VARCHAR(64) COMMENT '子分类',
    
    -- 元数据
    metadata JSON,
    tags JSON,
    
    -- 时间维度
    recorded_at DATETIME NOT NULL,
    time_window VARCHAR(32) COMMENT 'realtime, hourly, daily',
    
    -- 告警
    threshold_value FLOAT COMMENT '阈值',
    is_alert BOOLEAN DEFAULT FALSE,
    alert_level VARCHAR(32) COMMENT 'info, warning, error, critical',
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_metric_name (metric_name),
    INDEX idx_category (category),
    INDEX idx_recorded_at (recorded_at)
);
```

---

### 9. knowledge_base - 知识库表

**用途：** 存储系统使用的知识条目

**主要字段：**

```sql
CREATE TABLE knowledge_base (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(256) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    summary VARCHAR(512) COMMENT '摘要',
    
    -- 分类
    category VARCHAR(64) NOT NULL COMMENT 'product, order, policy, faq',
    subcategory VARCHAR(64),
    tags JSON,
    keywords JSON,
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- 质量
    priority INT DEFAULT 0,
    quality_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    
    -- 使用统计
    view_count INT DEFAULT 0,
    use_count INT DEFAULT 0,
    helpful_count INT DEFAULT 0,
    not_helpful_count INT DEFAULT 0,
    
    -- 适用范围
    applicable_agents JSON COMMENT '适用的智能体',
    
    -- 版本控制
    version VARCHAR(32),
    previous_version_id VARCHAR(36),
    
    -- 维护信息
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    reviewed_by VARCHAR(64),
    reviewed_at DATETIME,
    
    -- 过期
    expires_at DATETIME,
    is_expired BOOLEAN DEFAULT FALSE,
    
    metadata JSON,
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_title (title),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
);
```

---

### 10. error_logs - 错误日志表

**用途：** 记录系统运行中的错误和异常

**主要字段：**

```sql
CREATE TABLE error_logs (
    id VARCHAR(36) PRIMARY KEY,
    error_type VARCHAR(128) NOT NULL,
    error_message TEXT NOT NULL,
    error_code VARCHAR(64),
    
    -- 级别
    severity VARCHAR(32) NOT NULL COMMENT 'debug, info, warning, error, critical',
    
    -- 来源
    source VARCHAR(128) COMMENT '错误来源',
    module VARCHAR(128) COMMENT '模块名称',
    function VARCHAR(128) COMMENT '函数名称',
    
    -- 上下文
    session_id VARCHAR(64),
    user_id VARCHAR(64),
    
    -- 详情
    stack_trace TEXT COMMENT '堆栈跟踪',
    request_data JSON,
    response_data JSON,
    
    -- 处理
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(64),
    resolved_at DATETIME,
    resolution_notes TEXT,
    
    metadata JSON,
    
    created_time DATETIME,
    updated_time DATETIME,
    
    INDEX idx_error_type (error_type),
    INDEX idx_severity (severity),
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id)
);
```

---

## 🔗 表关系图

```
users (1) ──────┬───────> (N) conversations
                └───────> (N) messages

conversations (1) ──┬──> (N) messages
                    ├──> (N) agent_outputs
                    └──> (N) message_feedbacks

messages (1) ───────┬──> (N) message_feedbacks
                    └──> (1) agent_outputs (optional)
```

---

## 📝 使用示例

### 创建所有表

```bash
cd /Users/zhulang/work/customer_service
python -m app.db.auto_create_tables create
```

### 重新创建所有表

```bash
python -m app.db.auto_create_tables recreate
```

### 删除所有表

```bash
python -m app.db.auto_create_tables drop
```

---

## 🎯 核心设计特点

### 1. 智能体输出追踪 ⭐

`agent_outputs` 表是核心，记录：
- ✅ 每个智能体的输入和输出
- ✅ 路由决策（router_agent）
- ✅ 工具调用详情
- ✅ 记忆使用情况
- ✅ 性能指标（处理时间、Token、成本）
- ✅ 执行顺序

**应用场景：**
- 调试智能体行为
- 分析路由准确性
- 追踪成本和性能
- 优化Prompt
- 审计和合规

### 2. 完整的会话追踪

`conversations` + `messages` + `agent_outputs` 三表联动：
- 会话级别统计
- 消息级别记录
- 智能体级别详情

### 3. 多维度统计

- **实时性能** - agent_performance（按小时/天/周）
- **业务指标** - agent_usage_stats（满意度、成功率）
- **系统监控** - system_metrics（全局指标）

### 4. 灵活的JSON字段

使用JSON存储：
- Token使用详情
- 工具调用记录
- 元数据
- 标签和配置

### 5. 时间序列支持

所有表都有：
- `created_time` - 创建时间
- `updated_time` - 更新时间
- 业务相关时间戳

---

## 🔍 查询示例

### 查询智能体的处理历史

```sql
SELECT 
    ao.agent_type,
    ao.input_text,
    ao.output_text,
    ao.processing_time,
    ao.total_tokens,
    ao.cost
FROM agent_outputs ao
WHERE ao.session_id = 'session_xxx'
ORDER BY ao.execution_order;
```

### 分析路由准确性

```sql
SELECT 
    target_agent,
    AVG(confidence) as avg_confidence,
    COUNT(*) as route_count
FROM agent_outputs
WHERE agent_type = 'router_agent'
    AND created_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY target_agent;
```

### 统计智能体成本

```sql
SELECT 
    agent_type,
    COUNT(*) as calls,
    SUM(total_tokens) as total_tokens,
    SUM(cost) as total_cost,
    AVG(processing_time) as avg_time
FROM agent_outputs
WHERE DATE(created_time) = CURDATE()
GROUP BY agent_type;
```

---

## 📊 索引策略

### 高频查询字段

- `user_id` - 用户相关查询
- `session_id` - 会话相关查询
- `agent_type` - 智能体分析
- 时间字段 - 时间范围查询

### 复合索引建议

```sql
-- 会话消息查询
CREATE INDEX idx_session_time ON messages(session_id, created_time);

-- 智能体性能分析
CREATE INDEX idx_agent_time ON agent_outputs(agent_type, created_time);

-- 用户活跃度分析
CREATE INDEX idx_user_active ON users(is_active, last_active_time);
```

---

## 🎓 总结

本数据库设计特别强化了**智能体输出追踪能力**，通过 `agent_outputs` 表详细记录每个智能体的执行过程，支持：

✅ **完整的调用链追踪**
✅ **精确的成本核算**
✅ **详细的性能分析**
✅ **路由决策审计**
✅ **工具使用统计**
✅ **记忆管理监控**


