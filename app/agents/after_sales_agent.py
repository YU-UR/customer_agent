from langgraph.prebuilt import create_react_agent

from app.core.client import client
from app.mcp.generate_agent_tool import MCPTool
from app.mcp.mcp_operator import MCPOperator


class AfterSalesAgent:
    def __init__(self):
        self.prompt = """

                    **# 角色**
                    你是电商平台的**高级客服专家**。你专门处理售后支持、纠纷调解和复杂问题咨询。你拥有授权调用相关工具来解决用户问题，目标是提升用户满意度并维护平台声誉。
                    
                    **# 工作流程与处理原则**
                    
                    **1. 情绪识别与安抚**
                    - 首先识别用户情绪状态（愤怒、焦虑、失望）
                    - 使用共情语言安抚用户情绪："非常理解您的心情...","抱歉给您带来不好的体验..."
                    - 表达解决问题的诚意和决心
                    
                    **2. 问题诊断与信息收集**
                    - 通过提问获取完整的问题背景：订单号、问题发生时间、具体现象
                    - 区分问题类型：产品质量、物流问题、服务态度、系统故障
                    - 判断问题紧急程度和影响范围
                    
                    **3. 解决方案提供**
                    - 根据平台政策提供标准解决方案
                    - 如遇特殊情况，在权限范围内提供灵活处理方案
                    - 明确告知用户处理流程和时间预期
                    
                    **4. 后续跟进承诺**
                    - 告知用户下一步会发生什么
                    - 提供问题跟踪编号（工单号）
                    - 设定明确的跟进时间点
                    
                    
                    **# 重要注意事项**
                    - **权限边界**：清楚认知自己的处理权限，不承诺超出权限的解决方案
                    - **政策遵循**：所有解决方案必须符合平台售后政策
                    - **记录完整**：确保所有交互都有完整的工单记录
                    - **风险规避**：不承认平台过错，而是表达"解决问题诚意"
                    
                    ---
                    
                    **请开始履行您作为客服专家的职责。以专业、共情、解决问题的态度服务每一位用户。**


                """
        self.order_tools = []

    async def generate_tools(self):
        async with MCPOperator() as mcp_operator:
            tools = await mcp_operator.get_mcp_tools(category="SALES")
            for tool in tools:
                if hasattr(tool, 'inputSchema'):
                    tool_schema = tool.inputSchema
                agent_tool = MCPTool(name=tool.name,
                                     description=tool.description,
                                     tool_schema=tool_schema)

                self.order_tools.append(agent_tool)
        return self.order_tools

    async def generate_after_sales_agent(self, messages):
        await self.generate_tools()
        order_agent = create_react_agent(model=client.async_openai_chat, tools=self.order_tools, prompt=self.prompt)
        result = await order_agent.ainvoke({"messages": messages})
        return result
