"""
增强版多智能体API - 集成数据库记录功能

START
  ↓
conversation_start_node   ← 新增（会话建档）
  ↓
memory_loader
  ↓
router_enhanced           ← 记录路由日志
  ↓
tool_loader
  ↓
agent_enhanced            ← 记录agent执行日志
  ↓
memory_saver
  ↓
END
"""
from operator import add
from typing import TypedDict, Annotated, Any, Literal, Optional
import uuid
import time
from datetime import datetime

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, add_messages, START, END

from app.agents.base import RouterAgent
from app.agents.general_agent import GeneralAgent
from app.agents.order_agent import OrderAgent
from app.agents.product_agent import ProductAgent
from app.agents.after_sales_agent import AfterSalesAgent
from app.agents.promotion_agent import PromotionAgent
from app.memory.memory_operator import MemoryOperator
from app.mcp.tool_manager import tool_manager, get_available_tools

# 导入服务层
from app.services.integration_service import integration_service
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


class CustomerState(TypedDict):
    """客户服务状态管理（增强版）"""
    messages: Annotated[list[AnyMessage], add_messages]
    router_result: Any  # 路由结果
    current_agent: str  # 当前处理的agent
    final_response: str  # 最终响应
    user_id: str  # 用户ID
    session_id: str  # 会话ID
    memory_context: str  # 记忆上下文
    historical_memories: list  # 历史记忆列表
    available_tools: list  # 可用的MCP工具列表
    tool_results: dict  # 工具调用结果
    # 新增字段用于数据库记录
    conversation_started: bool  # 会话是否已开始记录
    processing_times: dict  # 处理时间记录
    current_message_id: str  # 当前消息ID


# 会话启动节点（新增）
"""
记录：
integration_service.record_conversation_start()
integration_service.record_user_message()
会话开始时间
第一条用户问题
session_id
📌 相当于：
“聊天日志系统开始建档”
"""
async def conversation_start_node(state: CustomerState):
    """会话启动节点：初始化会话记录"""
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    messages = state.get("messages", [])
    
    if not user_id or not session_id:
        return {"conversation_started": False}
    
    # 获取第一条用户消息
    first_question = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            first_question = msg.content
            break
    
    if not first_question:
        return {"conversation_started": False}
    
    try:
        # 记录会话开始
        result = await integration_service.record_conversation_start(
            session_id=session_id,
            user_id=user_id,
            first_question=first_question
        )
        
        # 记录用户消息
        message_id = await integration_service.record_user_message(
            session_id=session_id,
            user_id=user_id,
            message=first_question
        )
        
        logger.info(f"Conversation started and recorded: {session_id}")
        
        return {
            "conversation_started": True,
            "current_message_id": message_id,
            "processing_times": {}
        }
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}", exc_info=True)
        return {"conversation_started": False}


# 记忆加载节点
async def memory_loader_node(state: CustomerState):
    """记忆加载节点：在处理前加载用户的历史记忆"""
    user_id = state.get("user_id")
    current_message = state["messages"][-1].content if state["messages"] else ""

    if not user_id:
        return {"memory_context": "", "historical_memories": []}

    try:
        memory_operator = MemoryOperator()

        # 搜索相关的历史记忆
        relevant_memories = await memory_operator.search_memory(
            query=current_message,
            user_id=user_id,
            agent_id="customer_service"
        )

        # 获取最近的对话记忆
        recent_memories = await memory_operator.get_memory(
            user_id=user_id,
            agent_id="customer_service"
        )

        # 构建记忆上下文
        memory_context = ""
        if relevant_memories:
            memory_context += "相关历史记忆:\n"
            for memory in relevant_memories[:3]:  # 取前3个最相关的记忆
                memory_context += f"- {memory.get('memory', '')}\n"

        if recent_memories:
            memory_context += "\n最近对话记录:\n"
            for memory in recent_memories[-2:]:  # 取最近2条记录
                memory_context += f"- {memory.get('memory', '')}\n"

        return {
            "memory_context": memory_context,
            "historical_memories": relevant_memories
        }

    except Exception as e:
        logger.error(f"记忆加载失败: {e}", exc_info=True)
        return {"memory_context": "", "historical_memories": []}


# 工具加载节点
async def tool_loader_node(state: CustomerState):
    """工具加载节点：根据当前agent类型加载相应的MCP工具"""
    current_agent = state.get("current_agent", "")
    
    try:
        # 根据agent类型获取相应分类的工具
        category_mapping = {
            "order_agent": "ORDER",
            "product_agent": "PRODUCT", 
            "after_sales_agent": "AFTER_SALES",
            "promotion_agent": "PROMOTION",
            "general_agent": "SYSTEM"
        }
        
        category = category_mapping.get(current_agent, "SYSTEM")
        available_tools = await get_available_tools(category)
        
        # 转换为简化的工具信息
        tool_list = []
        for tool in available_tools:
            tool_list.append({
                "name": tool.name,
                "description": tool.description
            })
        
        return {
            "available_tools": tool_list,
            "tool_results": {}
        }
        
    except Exception as e:
        logger.error(f"工具加载失败: {e}", exc_info=True)
        return {
            "available_tools": [],
            "tool_results": {}
        }


# 路由节点（增强版）
"""
integration_service.record_router_decision(...)
记录：
用户输入
router判断结果
处理耗时
📌 相当于：
“这个问题为什么被分到 product_agent，是可以追溯的”
"""
async def router_node_enhanced(state: CustomerState):
    """路由节点：分析用户意图并记录路由决策"""
    messages = state["messages"]
    memory_context = state.get("memory_context", "")
    user_id = state.get("user_id")
    session_id = state.get("session_id")

    # 记录开始时间
    start_time = time.time()
    
    # 如果有记忆上下文，添加到消息中
    router = RouterAgent()
    if memory_context:
        router.prompt += "用户的记忆信息：" + "\n" + memory_context

    result = await router.run(messages)
    
    # 计算处理时间
    processing_time = time.time() - start_time

    if result["success"]:
        router_data = result["data"][0]  # 取第一个路由结果
        
        # 记录路由决策到数据库
        try:
            input_text = messages[-1].content if messages else ""
            await integration_service.record_router_decision(
                session_id=session_id,
                user_id=user_id,
                input_text=input_text,
                router_result=router_data,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Error recording router decision: {e}", exc_info=True)
        
        # 更新处理时间记录
        processing_times = state.get("processing_times", {})
        processing_times['router'] = processing_time
        
        return {
            "router_result": router_data,
            "current_agent": router_data["target_agent"],
            "processing_times": processing_times
        }
    else:
        # 路由失败，默认使用general_agent
        return {
            "router_result": {
                "target_agent": "general_agent",
                "confidence": 0.5,
                "user_intent": "通用咨询",
                "original_query": str(messages[-1].content if messages else "")
            },
            "current_agent": "general_agent"
        }


# 创建增强的agent节点函数
"""
记录：
integration_service.record_agent_response(...)
输入问题
agent输出
agent类型（order/product）
memory是否命中
耗时
prompt上下文
📌 相当于：
“每个AI回答都被数据库完整记录（可审计）”
"""
def create_enhanced_agent_node(agent_class, agent_method_name, agent_type: str, agent_name: str):
    """创建增强的agent节点，包含数据库记录"""

    async def enhanced_agent_node(state: CustomerState):
        messages = state["messages"]
        memory_context = state.get("memory_context", "")
        user_id = state.get("user_id")
        session_id = state.get("session_id")
        message_id = state.get("current_message_id")

        # 记录开始时间
        start_time = time.time()
        
        try:
            agent = agent_class()
            if memory_context:
                agent.prompt += "用户的记忆信息：" + "\n" + memory_context
            
            method = getattr(agent, agent_method_name)
            result = await method(messages)

            # 提取AI响应
            ai_response = result["messages"][-1].content if result["messages"] else f"抱歉，{agent_class.__name__}处理出现问题。"
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 记录智能体响应到数据库
            try:
                input_text = messages[-1].content if messages else ""
                await integration_service.record_agent_response(
                    session_id=session_id,
                    user_id=user_id,
                    message_id=message_id,
                    agent_type=agent_type,
                    agent_name=agent_name,
                    input_text=input_text,
                    output_text=ai_response,
                    processing_time=processing_time,
                    memory_context=memory_context if memory_context else None,
                    memory_used=bool(memory_context),
                    metadata={
                        "agent_class": agent_class.__name__,
                        "method": agent_method_name
                    }
                )
            except Exception as e:
                logger.error(f"Error recording agent response: {e}", exc_info=True)

            return {
                "messages": [AIMessage(content=ai_response)],
                "final_response": ai_response
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_response = f"抱歉，服务处理出现问题：{str(e)}"
            
            logger.error(f"Agent {agent_name} error: {e}", exc_info=True)
            
            return {
                "messages": [AIMessage(content=error_response)],
                "final_response": error_response
            }

    return enhanced_agent_node


# 创建各个增强的agent节点
order_agent_node_enhanced = create_enhanced_agent_node(
    OrderAgent, "generate_order_agent", "order_agent", "订单专家"
)
product_agent_node_enhanced = create_enhanced_agent_node(
    ProductAgent, "generate_product_agent", "product_agent", "商品顾问"
)
after_sales_agent_node_enhanced = create_enhanced_agent_node(
    AfterSalesAgent, "generate_after_sales_agent", "after_sales_agent", "售后专家"
)
promotion_agent_node_enhanced = create_enhanced_agent_node(
    PromotionAgent, "generate_promotion_agent", "promotion_agent", "优惠专员"
)
general_agent_node_enhanced = create_enhanced_agent_node(
    GeneralAgent, "generate_general_agent", "general_agent", "客服助手"
)


# 记忆保存节点
async def memory_saver_node(state: CustomerState):
    """记忆保存节点：在对话结束后保存记忆"""
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    messages = state.get("messages", [])

    if not user_id or not messages:
        return {}

    try:
        memory_operator = MemoryOperator()

        # 构建要保存的消息格式
        conversation_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                conversation_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                conversation_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })

        # 保存对话记忆
        if conversation_messages:
            await memory_operator.add_memory(
                messages=conversation_messages,
                user_id=user_id,
                agent_id="customer_service",
                run_id=session_id
            )

        logger.info(f"成功保存用户 {user_id} 的对话记忆")

    except Exception as e:
        logger.error(f"保存记忆失败: {e}", exc_info=True)

    return {}


# 路由决策函数
def route_to_agent(state: CustomerState) -> Literal[
    "order_agent", "product_agent", "after_sales_agent", "promotion_agent", "general_agent"]:
    """根据路由结果决定下一个节点"""
    current_agent = state.get("current_agent", "general_agent")

    # 映射到实际的节点名称
    agent_mapping = {
        "order_agent": "order_agent",
        "product_agent": "product_agent",
        "after_sales_agent": "after_sales_agent",
        "promotion_agent": "promotion_agent",
        "general_agent": "general_agent",
        "END": "END"
    }

    return agent_mapping.get(current_agent, "general_agent")


# 构建增强版工作流图
def create_customer_service_workflow_enhanced():
    """创建增强版客户服务工作流（包含数据库记录）"""

    # 创建状态图
    workflow = StateGraph(CustomerState)

    # 添加节点
    workflow.add_node("conversation_start", conversation_start_node)  # 新增
    workflow.add_node("memory_loader", memory_loader_node)
    workflow.add_node("tool_loader", tool_loader_node)
    workflow.add_node("router", router_node_enhanced)  # 使用增强版
    workflow.add_node("order_agent", order_agent_node_enhanced)  # 使用增强版
    workflow.add_node("product_agent", product_agent_node_enhanced)  # 使用增强版
    workflow.add_node("after_sales_agent", after_sales_agent_node_enhanced)  # 使用增强版
    workflow.add_node("promotion_agent", promotion_agent_node_enhanced)  # 使用增强版
    workflow.add_node("general_agent", general_agent_node_enhanced)  # 使用增强版
    workflow.add_node("memory_saver", memory_saver_node)

    # 设置入口点：先启动会话记录，然后加载记忆，再路由
    workflow.add_edge(START, "conversation_start")
    workflow.add_edge("conversation_start", "memory_loader")
    workflow.add_edge("memory_loader", "router")

    # 添加条件边：根据路由结果选择agent，先加载工具
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "order_agent": "tool_loader",
            "product_agent": "tool_loader", 
            "after_sales_agent": "tool_loader",
            "promotion_agent": "tool_loader",
            "general_agent": "tool_loader",
            "END": END
        }
    )
    
    # 从工具加载节点到具体的agent节点
    workflow.add_conditional_edges(
        "tool_loader",
        lambda state: state.get("current_agent", "general_agent"),
        {
            "order_agent": "order_agent",
            "product_agent": "product_agent",
            "after_sales_agent": "after_sales_agent", 
            "promotion_agent": "promotion_agent",
            "general_agent": "general_agent"
        }
    )

    # 所有agent处理完后都保存记忆
    workflow.add_edge("order_agent", "memory_saver")
    workflow.add_edge("product_agent", "memory_saver")
    workflow.add_edge("after_sales_agent", "memory_saver")
    workflow.add_edge("promotion_agent", "memory_saver")
    workflow.add_edge("general_agent", "memory_saver")

    # 保存记忆后结束
    workflow.add_edge("memory_saver", END)

    # 编译工作流
    app = workflow.compile()
    return app


# 增强版处理函数
async def process_customer_query_enhanced(user_message: str, user_id: Optional[str] = None,
                                         session_id: Optional[str] = None) -> dict:
    """
    处理客户查询的主函数（增强版 - 包含数据库记录）
    
    Args:
        user_message: 用户输入的消息
        user_id: 用户ID，用于记忆管理和数据库记录
        session_id: 会话ID，用于记忆管理和数据库记录
        
    Returns:
        包含处理结果的字典
    """
    # 创建工作流
    app = create_customer_service_workflow_enhanced()

    # 生成默认ID
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"

    # 初始化状态
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "router_result": None,
        "current_agent": None,
        "final_response": None,
        "user_id": user_id,
        "session_id": session_id,
        "memory_context": "",
        "historical_memories": [],
        "conversation_started": False,
        "processing_times": {},
        "current_message_id": None
    }

    # 执行工作流
    result = await app.ainvoke(initial_state)

    return {
        "success": True,
        "user_message": user_message,
        "user_id": user_id,
        "session_id": session_id,
        "router_result": result.get("router_result"),
        "current_agent": result.get("current_agent"),
        "final_response": result.get("final_response"),
        "memory_context": result.get("memory_context"),
        "processing_times": result.get("processing_times"),
        "messages": result.get("messages", [])
    }


# 流式处理函数（增强版）
async def stream_customer_query_enhanced(user_message: str, user_id: Optional[str] = None, 
                                        session_id: Optional[str] = None):
    """
    流式处理客户查询（增强版 - 包含数据库记录）
    
    Args:
        user_message: 用户输入的消息
        user_id: 用户ID
        session_id: 会话ID
        
    Yields:
        处理过程中的状态更新
    """
    app = create_customer_service_workflow_enhanced()

    # 生成默认ID
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"

    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "router_result": None,
        "current_agent": None,
        "final_response": None,
        "user_id": user_id,
        "session_id": session_id,
        "memory_context": "",
        "historical_memories": [],
        "conversation_started": False,
        "processing_times": {},
        "current_message_id": None
    }

    async for chunk in app.astream(initial_state):
        yield chunk

