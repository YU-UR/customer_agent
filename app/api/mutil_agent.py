from operator import add
from typing import TypedDict, Annotated, Any, Literal, Optional
import uuid

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

"""
❌ 没有记录：
router 做了什么决策
agent耗时
每一步调用日志
message级别审计
会话开始记录

START → memory_loader → router → agent → memory_saver
"""
class CustomerState(TypedDict):
    """客户服务状态管理"""
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
        print(f"记忆加载失败: {e}")
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
        print(f"工具加载失败: {e}")
        return {
            "available_tools": [],
            "tool_results": {}
        }


# 路由节点（增强版，包含记忆上下文）
async def router_node(state: CustomerState):
    """路由节点：分析用户意图并决定使用哪个agent"""
    messages = state["messages"]
    memory_context = state.get("memory_context", "")

    # 如果有记忆上下文，添加到消息中
    router = RouterAgent()
    if memory_context:
        router.prompt += "用户的记忆信息：" + "\n" + memory_context

    try:
        result = await router.run(messages)
        if result["success"]:
            router_data = result["data"][0]
            return {
                "router_result": router_data,
                "current_agent": router_data["target_agent"]
            }
    except Exception:
        pass
    return {
        "router_result": {
            "target_agent": "general_agent",
            "confidence": 0.5,
            "user_intent": "通用咨询",
            "original_query": str(messages[-1].content if messages else "")
        },
        "current_agent": "general_agent"
    }


# 增强的agent节点函数，包含记忆上下文
def create_enhanced_agent_node(agent_class, agent_method_name):
    """创建增强的agent节点，包含记忆上下文"""

    async def enhanced_agent_node(state: CustomerState):
        messages = state["messages"]
        memory_context = state.get("memory_context", "")

        try:
            agent = agent_class()
            if memory_context:
                agent.prompt += "用户的记忆信息：" + "\n" + memory_context
            method = getattr(agent, agent_method_name)
            result = await method(messages)

            # 提取AI响应
            ai_response = result["messages"][-1].content if result[
                "messages"] else f"抱歉，{agent_class.__name__}处理出现问题。"

            return {
                "messages": [AIMessage(content=ai_response)],
                "final_response": ai_response
            }
        except Exception as e:
            error_response = f"抱歉，服务处理出现问题：{str(e)}"
            return {
                "messages": [AIMessage(content=error_response)],
                "final_response": error_response
            }

    return enhanced_agent_node


# 创建各个增强的agent节点
order_agent_node = create_enhanced_agent_node(OrderAgent, "generate_order_agent")
product_agent_node = create_enhanced_agent_node(ProductAgent, "generate_product_agent")
after_sales_agent_node = create_enhanced_agent_node(AfterSalesAgent, "generate_after_sales_agent")
promotion_agent_node = create_enhanced_agent_node(PromotionAgent, "generate_promotion_agent")
general_agent_node = create_enhanced_agent_node(GeneralAgent, "generate_general_agent")


# 记忆保存节点
async def memory_saver_node(state: CustomerState):
    """记忆保存节点：在对话结束后保存记忆"""
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    messages = state.get("messages", [])
    current_agent = state.get("current_agent")

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

        print(f"成功保存用户 {user_id} 的对话记忆")

    except Exception as e:
        print(f"保存记忆失败: {e}")

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


# 构建工作流图（增强版）
def create_customer_service_workflow():
    """创建客户服务工作流（包含记忆功能）"""

    # 创建状态图
    workflow = StateGraph(CustomerState)

    # 添加节点
    workflow.add_node("memory_loader", memory_loader_node)
    workflow.add_node("tool_loader", tool_loader_node)
    workflow.add_node("router", router_node)
    workflow.add_node("order_agent", order_agent_node)
    workflow.add_node("product_agent", product_agent_node)
    workflow.add_node("after_sales_agent", after_sales_agent_node)
    workflow.add_node("promotion_agent", promotion_agent_node)
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("memory_saver", memory_saver_node)

    # 设置入口点：先加载记忆，然后路由
    workflow.add_edge(START, "memory_loader")
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

    workflow.add_edge("memory_saver", END)

    # 编译工作流

    app = workflow.compile()
    return app


# 主要的客户服务处理函数（增强版）
async def process_customer_query(user_message: str, user_id: Optional[str] = None,
                                 session_id: Optional[str] = None) -> dict:
    """
    处理客户查询的主函数（包含记忆功能）
    
    Args:
        user_message: 用户输入的消息
        user_id: 用户ID，用于记忆管理
        session_id: 会话ID，用于记忆管理
        
    Returns:
        包含处理结果的字典
    """
    # 创建工作流
    app = create_customer_service_workflow()

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
        "historical_memories": []
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
        "messages": result.get("messages", [])
    }


# 流式处理函数（增强版）
async def stream_customer_query(user_message: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
    """
    流式处理客户查询（包含记忆功能）
    
    Args:
        user_message: 用户输入的消息
        user_id: 用户ID，用于记忆管理
        session_id: 会话ID，用于记忆管理
        
    Yields:
        处理过程中的状态更新
    """
    app = create_customer_service_workflow()

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
        "historical_memories": []
    }

    async for chunk in app.astream(initial_state):
        yield chunk


# 记忆管理辅助函数
async def get_user_memory_summary(user_id: str) -> dict:
    """获取用户记忆摘要"""
    try:
        memory_operator = MemoryOperator()
        memories = await memory_operator.get_memory(user_id=user_id, agent_id="customer_service")

        return {
            "success": True,
            "user_id": user_id,
            "memory_count": len(memories),
            "memories": memories
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def clear_user_memory(user_id: str) -> dict:
    """清除用户记忆"""
    try:
        memory_operator = MemoryOperator()
        result = await memory_operator.delete_user_memory(user_id=user_id, agent_id="customer_service")

        return {
            "success": True,
            "user_id": user_id,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == '__main__':
    create_customer_service_workflow()
