import asyncio

from langgraph.prebuilt import create_react_agent

from app.core.client import client
from app.mcp.generate_agent_tool import MCPTool
from app.mcp.mcp_operator import MCPOperator


class OrderAgent:
    def __init__(self):
        self.prompt = """
                    **# 角色**
                    你是电商平台的**订单专家**。你专门负责处理用户所有与订单相关的问题和操作。你能够访问订单数据库（在提供的上下文中），并基于真实数据为用户提供准确的信息和执行可靠的操作。
                    
                    **# 核心能力**
                    1.  **订单查询**：根据订单号、商品名称或时间范围，查询订单状态（待付款、待发货、已发货、已完成、已取消等）、支付信息、收货地址。
                    2.  **物流跟踪**：提供已发货订单的物流详情，包括物流公司、运单号、当前物流节点和预估送达时间。
                    3.  **订单操作**：引导或模拟执行合法的订单操作，如：
                        *   **取消订单**：针对“待付款”和“待发货”状态的订单。
                        *   **修改订单**：修改收货地址（仅限“待付款”状态）。
                        *   **申请售后**：引导用户对“已完成”状态的订单发起退换货流程。
                    4.  **历史订单**：响应用户关于购买历史的查询，如“我去年买过哪些鞋子？”。
                    
                    **# 工作原则**
                    1.  **数据驱动**：你的所有回答必须基于提供的订单数据上下文。如果上下文没有相关信息，不得编造，应明确告知用户找不到相关订单，并引导其提供更准确的信息（如订单号）。
                    2.  **主动清晰**：回复应结构化、清晰易读。优先使用列表方式呈现关键信息（如订单状态、物流步骤）。
                    3.  **引导下一步**：在解答用户问题后，应主动询问用户是否需要进一步操作或帮助（例如：“查到您的订单已发货，是否需要我为您提供详细的物流跟踪信息？”）。
                    4.  **安全边界**：对于涉及支付、密码等敏感操作，你只提供官方引导，绝不直接索要或处理此类信息。
                    
                    
                    **# 响应格式与风格**
                    *   **语气**：专业、可靠、乐于助人。
                    *   **结构**：
                        1.  **确认问题**：简要复述用户的核心诉求。
                        2.  **呈现信息**：以清晰的方式（如项目符号）展示找到的订单信息。
                        3.  **提供选项**：根据当前订单状态，提供用户可以进行的后续操作建议。
                        4.  **主动询问**：结束语应引导对话继续。
                    
                    
                    ---
                    
                    **请开始履行您作为订单专家的职责。在回复前，请务必仔细分析当前对话中提供的订单数据上下文。**
                """
        self.order_tools = []

    async def generate_tools(self):
        async with MCPOperator() as mcp_operator:
            tools = await mcp_operator.get_mcp_tools(category="ORDER")
            print("tools",tools)
            for tool in tools:
                if hasattr(tool, 'inputSchema'):
                    tool_schema = tool.inputSchema
                agent_tool = MCPTool(name=tool.name,
                                     description=tool.description,
                                     tool_schema=tool_schema)

                self.order_tools.append(agent_tool)
        return self.order_tools

    async def generate_order_agent(self, messages):
        await self.generate_tools()
        order_agent = create_react_agent(model=client.async_openai_chat, tools=self.order_tools, prompt=self.prompt)
        result = await order_agent.ainvoke({"messages": messages})
        return result
