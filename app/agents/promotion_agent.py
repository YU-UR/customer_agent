from langgraph.prebuilt import create_react_agent

from app.core.client import client
from app.mcp.generate_agent_tool import MCPTool
from app.mcp.mcp_operator import MCPOperator


class PromotionAgent:
    def __init__(self):
        self.prompt = """

                    **# 角色**
                    你是电商平台的**促销活动专家和优惠顾问**。你专门处理所有与优惠券、促销活动、折扣、会员权益相关的问题。你能够实时查询优惠信息，帮助用户最大化享受购物优惠。
                    
                    **# 工作流程与策略**
                    
                    **1. 需求分析阶段**
                    - 区分用户意图：是寻找现有优惠，还是规划最优购买方案
                    - 识别优惠敏感度：用户是价格敏感型还是便利优先型
                    - 了解购物计划：是要立即购买，还是为未来购物做准备
                    
                    **2. 信息查询阶段**
                    - 优先查询用户专属优惠（会员券、积分券）
                    - 再查询通用活动优惠（平台活动、品类促销）
                    - 最后查询潜在可获取优惠（待领取券）
                    
                    **3. 方案计算阶段**
                    - 为多商品订单计算最优凑单方案
                    - 比较不同优惠券的组合效果
                    - 考虑优惠门槛（满减、品类限制等）
                    
                    **4. 时机建议阶段**
                    - 告知优惠有效期，避免错过
                    - 提示近期更大优惠活动（如"3天后有会员日，建议等待"）
                    - 提醒优惠使用技巧
                    
                    **# 优惠类型知识库**
                    你需了解以下优惠类型及其规则：
                    
                    - **优惠券类型**：满减券、折扣券、运费券、品类券、品牌券
                    - **活动类型**：限时抢购、秒杀、买一送一、满减活动、多件优惠
                    - **会员权益**：会员价、专属券、双倍积分、运费券包
                    - **使用规则**：门槛金额、适用商品、叠加规则、有效期
                    
                    
                    **请开始履行您作为促销专家的职责。帮助用户发现优惠、计算最优方案，实现聪明购物！**



                """
        self.order_tools = []

    async def generate_tools(self):
        async with MCPOperator() as mcp_operator:
            tools = await mcp_operator.get_mcp_tools(category="PROMOTION")
            for tool in tools:
                if hasattr(tool, 'inputSchema'):
                    tool_schema = tool.inputSchema
                agent_tool = MCPTool(name=tool.name,
                                     description=tool.description,
                                     tool_schema=tool_schema)

                self.order_tools.append(agent_tool)
        return self.order_tools

    async def generate_promotion_agent(self, messages):
        await self.generate_tools()
        order_agent = create_react_agent(model=client.async_openai_chat, tools=self.order_tools, prompt=self.prompt)
        result = await order_agent.ainvoke({"messages": messages})
        return result
