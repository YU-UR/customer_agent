# Intelligent E-commerce Customer Service & Sales Support System

## 📋 Project Overview

The Intelligent E-commerce Customer Service & Sales Support System is a modern customer service solution based on multi-agent architecture and MCP (Model Context Protocol), designed to provide efficient, intelligent, and personalized customer service experiences for e-commerce platforms. The system adopts a dual-service architecture (MCP server on port 8000, main application service on port 8001) and leverages advanced AI technology through collaborative specialized agents to deliver 24/7 uninterrupted customer service support.

## 🏗️ System Architecture

### Multi-Agent Architecture Design

The system adopts a distributed multi-agent architecture where each agent focuses on specific business domains, achieving efficient customer service through intelligent routing and collaboration mechanisms:

```
                    ┌─────────────────────────────────────┐
                    │           User Interface            │
                    │        Interaction Layer           │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │         Router Agent                │
                    │       Intent Recognition            │
                    │      & Request Routing             │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────┴────────┐    ┌──────────────┴─────────────┐    ┌──────────┴─────────┐
│ Product Agent  │    │      Order Agent           │    │ Promotion Agent    │
│Product Inquiry │    │   Order Management         │    │ Campaign & Offers  │
│& Recommendation│    │    & Tracking              │    │   Management       │
└───────┬────────┘    └──────────────┬─────────────┘    └──────────┬─────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │     After-sales Agent               │
                    │   Returns, Exchanges &              │
                    │    Complaint Handling               │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────┴────────┐    ┌──────────────┴─────────────┐    ┌──────────┴─────────┐
│ RAG Retrieval  │    │    Memory Management       │    │   Vector Database  │
│ Embedding &    │    │       System               │    │   Milvus Vector    │
│ Vector Search  │    │ Long-term Memory & Context │    │     Storage        │
└────────────────┘    └────────────────────────────┘    └───────────────────┘
```

### Core Components

#### 🧠 Agent Layer
- **Router Agent**: Natural language understanding-based user intent recognition and intelligent request routing
- **Product Agent**: Handles product inquiries, intelligent recommendations, comparative analysis, and inventory queries
- **Order Agent**: Manages the complete order lifecycle including queries, tracking, modifications, and exception handling
- **Promotion Agent**: Processes promotional activities, campaign information, coupon management, and membership benefits
- **After-sales Agent**: Responsible for return/exchange processes, complaint handling, and customer satisfaction management

#### 🔍 Data & Memory Layer
- **RAG Retrieval System**: Vector similarity-based knowledge retrieval supporting hybrid dense and sparse vector search
- **Memory Management System**: Long-term memory management based on MEM0 framework, maintaining user preferences and conversation history
- **Vector Database**: Milvus vector database supporting high-performance semantic search and similarity matching

#### ⚙️ Technical Support Layer
- **Asynchronous Processing Engine**: High-concurrency asynchronous processing architecture based on asyncio
- **MCP Protocol Support**: Model Context Protocol supporting tool invocation and external system integration
- **Configuration Management System**: Unified configuration management and environment variable processing

## ✨ Core Features

### 🤖 Intelligent Dialogue System
- **Natural Language Understanding**: Accurate user intent comprehension with multi-turn conversation support
- **Context Maintenance**: Maintains conversation coherence and remembers user preferences
- **Multi-modal Interaction**: Supports text, images, and other interaction modes

### 🛍️ Product Services
- **Intelligent Search**: Semantic understanding-based product search
- **Personalized Recommendations**: Product recommendations based on user behavior and preferences
- **Detailed Consultation**: Comprehensive product specifications, pricing, and inventory information
- **Comparative Analysis**: Multi-product comparison and pros/cons analysis

### 📦 Order Management
- **Real-time Queries**: Real-time order status and logistics tracking
- **Order Operations**: Support for order modifications, cancellations, and other operations
- **Exception Handling**: Automatic identification and handling of order anomalies
- **Historical Records**: Complete order history queries

### 🔧 After-sales Service
- **Returns & Exchanges**: Automated return and exchange process guidance
- **Quality Issues**: Intelligent diagnosis and solution recommendations
- **Complaint Handling**: Standardized complaint processing workflows
- **Satisfaction Surveys**: Automated customer satisfaction collection

## 🛠️ Technology Stack

### 🐍 Backend Framework
- **Python 3.12+**: Primary development language with modern asynchronous programming support (Recommended to use Conda for environment management)
- **FastAPI**: High-performance asynchronous web framework with automatic API documentation
- **Uvicorn**: ASGI server supporting high-concurrency processing
- **Pydantic**: Data validation and serialization with type safety guarantees

### 🤖 AI/ML Technology Stack
- **LangGraph**: Multi-agent workflow orchestration and state management
- **LangChain**: LLM application development framework with tool calling and chain processing
- **OpenAI GPT-4**: Primary language model with function calling support
- **DeepSeek**: Alternative language model for cost optimization
- **DashScope**: Alibaba Cloud's model service for text embedding generation
- **MCP (Model Context Protocol)**: Standardized tool integration protocol (MCP server runs on port 8000, main application service runs on port 8001, supports SSE real-time communication)

### 🔍 Vector Retrieval & Memory
- **Milvus**: High-performance vector database supporting hybrid retrieval
- **MEM0**: Long-term memory management framework for personalized user experience
- **RAG (Retrieval-Augmented Generation)**: Retrieval-enhanced generation
- **Dense & Sparse Vectors**: Hybrid dense and sparse vector search
- **Semantic Search**: Semantic search and similarity computation

### 💾 Data Storage
- **MySQL 8.0+**: Primary relational database with transaction support
- **Redis**: High-performance caching and session storage
- **Vector Database**: Dedicated vector storage and retrieval
- **Memory Store**: User memory and preference storage

### 🔧 Development & Deployment
- **Docker & Docker Compose**: Containerized deployment and service orchestration
- **Poetry**: Modern Python dependency management
- **Pytest**: Comprehensive unit testing framework
- **Black & isort**: Code formatting and import sorting
- **Pre-commit**: Git hooks and code quality checks

### 🌐 Integration & Monitoring
- **JWT**: Secure user authentication and authorization
- **Logging**: Structured logging and monitoring
- **Environment Config**: Environment variable configuration management
- **Health Checks**: Service health monitoring and checks

## 📦 Installation Guide

### System Requirements

- Python 3.12+ (Recommended to use conda for management)
- MySQL 8.0+ or higher
- Redis 6.0+ or higher
- Milvus 2.0+ or higher

### Quick Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-repo/customer_service.git
cd customer_service
```

2. **Create Conda Virtual Environment**
```bash
# Create conda environment named customer_service
conda create -n customer_service python=3.12
conda activate customer_service
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env file to configure database connections and API keys
# Note: Main application runs on port 8001, MCP server runs on port 8000
```

5. **Start Services**

**Method 1: Using Startup Scripts (Recommended)**
```bash
# Start MCP server (in a new terminal)
conda activate customer_service
python app/mcp/mcp_server.py

# Start main application (in another terminal)
conda activate customer_service
python start.py
```

**Method 2: Start Separately**
```bash
# Terminal 1: Start MCP server
conda activate customer_service
python app/mcp/mcp_server.py
# MCP server will run on http://127.0.0.1:8000

# Terminal 2: Start main application
conda activate customer_service
python start.py
# Main application will run on http://0.0.0.0:8001
```

6. **Verify Installation**
```bash
# Access API documentation
curl http://localhost:8001/docs
# Or open http://localhost:8001/docs in browser

# Check MCP server status
curl http://localhost:8000/health
```

### Docker Deployment

```bash
# Build image
docker build -t customer-service .

# Run container
docker run -d \
  --name customer-service \
  -p 8001:8001 \
  -p 8000:8000 \
  -e DATABASE_URL="mysql://user:password@host:port/database" \
  -e REDIS_URL="redis://host:port" \
  -e PORT=8001 \
  -e MCP_PORT=8000 \
  customer-service

# Or use docker-compose
docker-compose up -d
```

## 🚀 Usage Guide

### Basic Configuration

Configure the following key parameters in the `.env` file:

```env
# Application Configuration
APP_NAME=Intelligent E-commerce Customer Service & Sales Support System
DEBUG=false
HOST=0.0.0.0
PORT=8001
MCP_PORT=8000

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=customer_service

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

### API Usage Examples

#### 🔄 Basic Chat API
```python
import httpx
import asyncio

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        # Send message to intelligent customer service
        response = await client.post(
            "http://localhost:8001/api/chat",
            json={
                "message": "I want to check my order status",
                "user_id": "user123",
                "session_id": "session456"
            }
        )
        
        result = response.json()
        print(f"Agent response: {result['response']}")
        print(f"Agent type used: {result['agent_type']}")
        print(f"Confidence: {result['confidence']}")

# Run example
asyncio.run(chat_with_agent())
```

#### 🛍️ Product Search API
```python
async def search_products():
    async with httpx.AsyncClient() as client:
        # Intelligent product search
        response = await client.post(
            "http://localhost:8001/api/products/search",
            json={
                "query": "warm winter coats for cold weather",
                "user_id": "user123",
                "filters": {
                    "price_range": [50, 200],
                    "category": "clothing"
                }
            }
        )
        
        products = response.json()
        for product in products['results']:
            print(f"Product: {product['name']}")
            print(f"Price: ${product['price']}")
            print(f"Recommendation reason: {product['recommendation_reason']}")
```

#### 📦 Order Management API
```python
async def track_order():
    async with httpx.AsyncClient() as client:
        # Order tracking
        response = await client.get(
            "http://localhost:8001/api/orders/track",
            params={
                "order_id": "ORD123456",
                "user_id": "user123"
            }
        )
        
        order_info = response.json()
        print(f"Order status: {order_info['status']}")
        print(f"Logistics info: {order_info['logistics']}")
        print(f"Estimated delivery: {order_info['estimated_delivery']}")
```

#### 🧠 Memory Management API
```python
async def get_user_preferences():
    async with httpx.AsyncClient() as client:
        # Get user preferences and history
        response = await client.get(
            "http://localhost:8001/api/memory/preferences",
            params={"user_id": "user123"}
        )
        
        preferences = response.json()
        print(f"User preferences: {preferences['preferences']}")
        print(f"Purchase history: {preferences['purchase_history']}")
        print(f"Interaction summary: {preferences['interaction_summary']}")
```

### Agent Usage

#### Router Agent
```python
from app.agents.base import RouterAgent

router = RouterAgent()
result = await router.run("I want to buy a smartphone")
# Output: {"target_agent": "product_agent", "confidence": 0.95}
```

#### Product Agent
```python
from app.agents.product_agent import ProductAgent

product_agent = ProductAgent()
response = await product_agent.generate_product_agent("Recommend a cost-effective smartphone")
```

## 🔧 Development Guide

### Project Structure

```
customer_service/
├── __init__.py            # Package initialization
├── app/                   # Main application directory
│   ├── __init__.py        # Package initialization
│   ├── api/               # API interfaces
│   │   └── mutil_agent.py # Multi-agent API endpoints
│   ├── mcp/               # MCP protocol support
│   │   ├── mcp_server.py  # MCP server (port 8000)
│   │   └── tool_manager.py # Tool management
│   ├── services/          # Business service layer
│   └── utils/             # Utility functions
│       └── log_utils.py   # Logging utilities
├── data/                  # Data storage directory
├── logs/                  # Log directory
├── temp/                  # Temporary files
├── QR_code/               # QR code generation
├── start.py               # Main application entry (port 8001)
├── requirements.txt       # Dependency list
├── README.md              # Chinese documentation
└── README.en.md           # English documentation
```

## 🛠️ Development Guide

### Service Architecture

The system adopts a dual-service architecture:

- **MCP Server** (port 8000): Handles tool management and MCP protocol communication
- **Main Application Service** (port 8001): Provides API interfaces and business logic
- **Communication**: Services communicate via HTTP/SSE for real-time data exchange

### Adding New Agents

1. Create a new agent file in the `app/services/` directory
2. Inherit from the base agent class and implement necessary methods
3. Add new routing rules in the multi-agent API
4. Update configuration and documentation

### Feature Extension

The system adopts modular design for flexible extension:

- **New Business Modules**: Add new modules in corresponding directories
- **Third-party Service Integration**: Integrate external tools through MCP protocol
- **Custom Agents**: Implement specialized agents for specific business scenarios

### Development & Debugging

```bash
# Start MCP server for development
conda activate customer_service
python app/mcp/mcp_server.py

# Start main application in development mode
conda activate customer_service
python start.py

# Run tests
pytest tests/

# Check code style
black app/
isort app/
```

### Code Standards

- Follow PEP 8 Python coding standards
- Add appropriate comments and docstrings
- Write unit tests
- Ensure code passes all tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

- **Issue Reports**: [GitHub Issues](https://github.com/YU-UR/customer_agent/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/YU-UR/customer_agent/discussions)

## 🙏 Acknowledgments

Thanks to the following open source projects for their support:

- [LangChain](https://github.com/langchain-ai/langchain) - AI application development framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern web framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

---

⭐ If this project helps you, please give us a star!

