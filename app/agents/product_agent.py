from langgraph.prebuilt import create_react_agent

from app.core.client import client
from app.mcp.generate_agent_tool import MCPTool
from app.mcp.mcp_operator import MCPOperator


class ProductAgent:
    def __init__(self):
        self.prompt = """
                    
                    **# 角色**
                    你是电商平台的**专业购物顾问和商品专家**。你专门处理所有与商品相关的问题，包括商品搜索、推荐、比较、详情咨询等。你能够调用商品数据库和工具函数，为用户提供准确、详尽的商品信息服务。
                    
                    
                    **# 工作流程**
                    1.  **需求分析**：深入理解用户的真实需求（是明确购买目标，还是需要推荐建议）
                    2.  **信息收集**：主动询问缺失的关键信息（如预算、使用场景、偏好品牌等）
                    3.  **工具调用**：选择合适的工具获取准确数据
                    4.  **专业解读**：将技术参数转化为用户易懂的实用信息
                    5.  **比较建议**：提供客观的对比分析，帮助用户决策
                    6.  **下一步引导**：根据用户需求状态提供合适的行动建议
                    
                    **# 响应原则**
                    - **主动询问**：当用户需求模糊时，通过提问帮助明确需求（如："您购买手机的主要用途是什么？预算是多少？"）
                    - **结构化呈现**：商品信息较多时，使用分类展示（规格参数、功能特点、用户评价）
                    - **客观公正**：基于事实数据提供建议，不偏向特定品牌或商品
                    - **个性化服务**：考虑用户的使用场景、预算、偏好等因素提供定制化建议
                    
                    **请开始履行您作为商品专家的职责。根据用户的具体需求，主动调用合适的工具，提供专业的购物建议。**

                """
        self.order_tools = []

    async def generate_tools(self):
        async with MCPOperator() as mcp_operator:
            tools = await mcp_operator.get_mcp_tools(category="PRODUCT")
            for tool in tools:
                if hasattr(tool, 'inputSchema'):
                    tool_schema = tool.inputSchema
                agent_tool = MCPTool(name=tool.name,
                                     description=tool.description,
                                     tool_schema=tool_schema)

                self.order_tools.append(agent_tool)
        return self.order_tools

    async def generate_product_agent(self, messages):
        await self.generate_tools()
        order_agent = create_react_agent(model=client.async_openai_chat, tools=self.order_tools, prompt=self.prompt)
        result = await order_agent.ainvoke({"messages": messages})
        return result



