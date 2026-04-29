# 智能电商客服与销售支持系统

## 📋 项目概述

智能电商客服与销售支持系统是一个基于多智能体架构的现代化客服解决方案。系统采用统一服务架构设计，集成了智能体路由、RAG检索增强生成、长期记忆管理和向量数据库技术。

## 🏗️ 系统架构

### 多智能体架构设计

系统采用分布式多智能体架构，每个智能体专注于特定的业务领域，通过智能路由和协作机制实现高效的客户服务：

```
                    ┌─────────────────────────────────────┐
                    │           用户交互层                 │
                    │        User Interface              │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │         路由智能体                   │
                    │       Router Agent                 │
                    │    (意图识别 & 请求分发)              │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────┴────────┐    ┌──────────────┴─────────────┐    ┌──────────┴─────────┐
│   产品智能体     │    │        订单智能体           │    │    促销智能体       │
│ Product Agent  │    │      Order Agent          │    │ Promotion Agent   │
│  商品咨询推荐    │    │     订单管理跟踪           │    │   活动优惠管理      │
└───────┬────────┘    └──────────────┬─────────────┘    └──────────┬─────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │        售后智能体                    │
                    │     After-sales Agent              │
                    │      退换货 & 投诉处理               │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────┴────────┐    ┌──────────────┴─────────────┐    ┌──────────┴─────────┐
│   RAG检索系统   │    │        记忆管理系统          │    │    向量数据库       │
│ Embedding &    │    │      Memory System         │    │   Milvus Vector   │
│ Vector Search  │    │   长期记忆 & 上下文管理       │    │     Database      │
└────────────────┘    └────────────────────────────┘    └───────────────────┘
```

### 核心组件

#### 🧠 智能体层
- **路由智能体 (Router Agent)**: 基于自然语言理解的用户意图识别和智能请求路由
- **产品智能体 (Product Agent)**: 处理商品咨询、智能推荐、比较分析和库存查询
- **订单智能体 (Order Agent)**: 管理订单全生命周期，包括查询、跟踪、修改和异常处理
- **促销智能体 (Promotion Agent)**: 处理优惠活动、促销信息、优惠券管理和会员权益
- **售后智能体 (After-sales Agent)**: 负责退换货流程、投诉处理和客户满意度管理

#### 🔍 数据与记忆层
- **RAG检索系统**: 基于向量相似度的知识检索，支持密集向量和稀疏向量混合搜索
- **记忆管理系统**: 基于MEM0框架的长期记忆管理，维护用户偏好和对话历史
- **向量数据库**: Milvus向量数据库，支持高性能的语义搜索和相似度匹配

#### ⚙️ 技术支撑层
- **异步处理引擎**: 基于asyncio的高并发异步处理架构
- **MCP协议支持**: 模型上下文协议，支持工具调用和外部系统集成
- **配置管理系统**: 统一的配置管理和环境变量处理

## ✨ 核心功能

### 🤖 智能对话系统
- **自然语言理解**: 准确理解用户意图，支持多轮对话
- **上下文维护**: 保持对话连贯性，记住用户偏好
- **多模态交互**: 支持文本、图片等多种交互方式

### 🛍️ 商品服务
- **智能搜索**: 基于语义理解的商品搜索
- **个性化推荐**: 根据用户行为和偏好推荐商品
- **详细咨询**: 提供商品规格、价格、库存等详细信息
- **比较分析**: 多商品对比和优劣势分析

### 📦 订单管理
- **实时查询**: 订单状态、物流信息实时跟踪
- **订单操作**: 支持订单修改、取消等操作
- **异常处理**: 自动识别和处理订单异常情况
- **历史记录**: 完整的订单历史查询

### 🔒 安全防护
- **API密钥验证**: 基于Bearer Token的API访问控制
- **输入验证与清理**: 防止XSS和注入攻击的输入过滤
- **请求限流**: 基于用户和IP的智能限流机制
- **安全响应头**: 完善的HTTP安全头配置
- **CORS保护**: 跨域请求的安全控制
- **异常处理**: 统一的异常处理和错误响应

## 🛠️ 技术栈

### 🐍 后端框架
- **Python 3.12+**: 主要开发语言，支持现代异步编程
- **FastAPI**: 高性能异步Web框架，支持自动API文档生成
- **Uvicorn**: ASGI服务器，支持高并发处理
- **Pydantic**: 数据验证和序列化，类型安全保障
- **Conda**: Python环境管理，推荐使用customer_service环境

### 🤖 AI/ML技术栈
- **LangGraph**: 多智能体工作流编排和状态管理
- **LangChain**: LLM应用开发框架，工具调用和链式处理
- **OpenAI GPT-4**: 主要语言模型，支持函数调用
- **DeepSeek**: 备用语言模型，成本优化选择
- **DashScope**: 阿里云灵积模型服务，文本嵌入生成
- **智能体工具集成**: 支持多种工具和外部服务集成
  - 主应用服务运行在端口8001
  - 支持RESTful API和流式响应
  - 完善的API文档和健康检查

### 🔍 向量检索与记忆
- **Milvus**: 高性能向量数据库，支持混合检索
- **MEM0**: 长期记忆管理框架，个性化用户体验
- **RAG (Retrieval-Augmented Generation)**: 检索增强生成
- **Dense & Sparse Vectors**: 密集和稀疏向量混合搜索
- **Semantic Search**: 语义搜索和相似度计算

### 💾 数据存储
- **MySQL 8.0+**: 主要关系型数据库，事务支持
- **Redis**: 高性能缓存和会话存储(可追加)
- **Vector Database**: 专用向量存储和检索
- **Memory Store**: 用户记忆和偏好存储

### 🔧 开发与部署
- **Docker & Docker Compose**: 容器化部署和服务编排

### 🌐 集成与监控
- **JWT**: 安全的用户认证和授权
- **Logging**: 结构化日志记录和监控
- **Environment Config**: 环境变量配置管理
- **Health Checks**: 服务健康检查和监控

## 📦 安装指南

### 环境要求

- **Python 3.12+** (强烈推荐使用conda环境管理)
- **Conda** (推荐使用Anaconda或Miniconda)
- MySQL 8.0+ 或更高版本
- Redis 6.0+ 或更高版本（可追加）
- Milvus 2.0+ 或更高版本

> **重要提示**: 本项目强烈建议在conda虚拟环境中运行，以确保依赖管理的稳定性和环境隔离。

### 快速安装

1. **克隆项目**
```bash
git clone https://github.com/YU-UR/customer_agent.git
cd customer_agent
```

2. **创建conda虚拟环境**
```bash
# 创建名为customer_service的conda环境
conda create -n customer_service python=3.12
conda activate customer_service
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接和API密钥
# 注意：主应用运行在端口8001，MCP服务器运行在端口8000
```

5. **启动服务**

```bash
# 确保在conda虚拟环境中
conda activate customer_service

# 启动智能客服系统
python -m app.main
```

应用将启动并运行在 `http://0.0.0.0:8001`

6. **验证安装**
```bash
# 访问API文档
curl http://localhost:8001/docs
# 或在浏览器中打开 http://localhost:8001/docs

# 检查服务健康状态
curl http://localhost:8001/health
```

### Docker 部署

```bash
# 构建镜像
docker build -t customer-service .

# 运行容器
docker run -d \
  --name customer-service \
  -p 8001:8001 \
  -e DATABASE_URL="mysql://user:password@host:port/database" \
  -e REDIS_URL="redis://host:port" \
  -e PORT=8001 \
  customer-service

# 或使用docker-compose
docker-compose up -d
```

## 🚀 使用指南

### 基本配置

在 `.env` 文件中配置以下关键参数：

```env
# 应用配置
APP_NAME=智能电商客服与销售支持系统
DEBUG=false
HOST=0.0.0.0
PORT=8001

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=customer_service

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# AI模型配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

### API 使用示例

#### 🔄 基础对话API
```python
import httpx
import asyncio

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        # 发送消息给智能客服
        response = await client.post(
            "http://localhost:8001/api/chat",
            json={
                "message": "我想查询我的订单状态",
                "user_id": "user123",
                "session_id": "session456"
            }
        )
        
        result = response.json()
        print(f"智能体回复: {result['response']}")
        print(f"使用的智能体: {result['agent_type']}")
        print(f"置信度: {result['confidence']}")

# 运行示例
asyncio.run(chat_with_agent())
```

#### 🛍️ 产品查询API
```python
async def search_products():
    async with httpx.AsyncClient() as client:
        # 智能产品搜索
        response = await client.post(
            "http://localhost:8001/api/products/search",
            json={
                "query": "适合冬天的保暖外套",
                "user_id": "user123",
                "filters": {
                    "price_range": [100, 500],
                    "category": "服装"
                }
            }
        )
        
        products = response.json()
        for product in products['results']:
            print(f"商品: {product['name']}")
            print(f"价格: ¥{product['price']}")
            print(f"推荐理由: {product['recommendation_reason']}")
```

#### 📦 订单管理API
```python
async def track_order():
    async with httpx.AsyncClient() as client:
        # 订单跟踪
        response = await client.get(
            "http://localhost:8001/api/orders/track",
            params={
                "order_id": "ORD123456",
                "user_id": "user123"
            }
        )
        
        order_info = response.json()
        print(f"订单状态: {order_info['status']}")
        print(f"物流信息: {order_info['logistics']}")
        print(f"预计送达: {order_info['estimated_delivery']}")
```

#### 🧠 记忆管理API
```python
async def get_user_preferences():
    async with httpx.AsyncClient() as client:
        # 获取用户偏好和历史
        response = await client.get(
            "http://localhost:8001/api/memory/preferences",
            params={"user_id": "user123"}
        )
        
        preferences = response.json()
        print(f"用户偏好: {preferences['preferences']}")
        print(f"购买历史: {preferences['purchase_history']}")
        print(f"互动记录: {preferences['interaction_summary']}")
```

### 智能体使用

#### 路由智能体
```python
from app.agents.base import RouterAgent

router = RouterAgent()
result = await router.run("我想买一台手机")
# 输出: {"target_agent": "product_agent", "confidence": 0.95}
```

#### 产品智能体
```python
from app.agents.product_agent import ProductAgent

product_agent = ProductAgent()
response = await product_agent.generate_product_agent("推荐一款性价比高的手机")
```

### 项目结构

```
customer_service/
├── app/                    # 应用主目录
│   ├── __init__.py        # 包初始化文件
│   ├── agents/            # 智能体模块
│   │   ├── base.py        # 路由智能体基类
│   │   ├── product_agent.py   # 产品智能体
│   │   ├── order_agent.py     # 订单智能体
│   │   ├── promotion_agent.py # 促销智能体
│   │   └── after_sales_agent.py # 售后智能体
│   ├── api/               # API接口层
│   │   └── mutil_agent.py # 多智能体API接口
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   └── client.py      # 客户端配置
│   ├── db/                # 数据库模块
│   ├── mcp/               # MCP协议支持
│   │   ├── mcp_server.py  # MCP服务器 (端口8000)
│   │   └── tool_manager.py # 工具管理器
│   ├── memory/            # 记忆系统
│   ├── models/            # 数据模型
│   ├── rag/               # RAG检索增强
│   ├── services/          # 业务服务层
│   ├── utils/             # 工具函数
│   │   └── log_utils.py   # 日志工具
│   └── main.py            # FastAPI应用入口
├── data/                  # 数据目录
├── logs/                  # 日志目录
│   └── app.log           # 应用日志文件
├── temp/                  # 临时文件目录
├── QR_code/              # 二维码资源
├── .env                   # 环境变量配置
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略文件
├── requirements.txt      # Python依赖列表
├── start.py              # 项目启动脚本 (端口8001)
├── LICENSE               # 许可证文件
├── README.md             # 项目文档 (中文)
├── README.en.md          # 项目文档 (英文)
└── 智能电商客服与销售支持系统需求文档.md # 需求文档
```

### 服务架构说明

系统采用统一服务架构：

1. **主应用服务** (`python -m app.main`)
   - 运行在端口8001
   - 提供完整的REST API接口
   - 集成智能体路由和工具管理
   - 支持流式响应和实时通信
   - 内置安全防护和监控功能

### 添加新智能体

1. 在 `app/agents/` 目录下创建新的智能体文件
2. 继承基础智能体类并实现必要方法
3. 在路由智能体 (`app/agents/base.py`) 中添加新的路由规则
4. 更新 `app/api/mutil_agent.py` 中的API接口
5. 更新配置和文档

### 扩展功能

系统采用模块化设计，支持灵活扩展：

- **新增业务模块**: 在相应目录下添加新模块
- **集成第三方服务**: 通过MCP协议集成外部工具
- **自定义智能体**: 实现特定业务场景的专用智能体
- **添加新工具**: 在 `app/mcp/tool_manager.py` 中注册新工具

### 开发调试

```bash
# 查看服务健康状态
curl http://localhost:8001/health

# 查看API文档
open http://localhost:8001/docs

# 查看日志
tail -f logs/app.log

# 重启服务
# Ctrl+C 停止服务，然后重新运行: python -m app.main
```
## 🙏 致谢

感谢以下开源项目的支持：

- [LangChain](https://github.com/langchain-ai/langchain) - AI应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 多智能体编排
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代Web框架
- [Pydantic](https://github.com/pydantic/pydantic) - 数据验证

