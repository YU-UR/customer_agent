import asyncio
from typing import Type

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from app.core.client import client
from app.rag.embedding_operator import query_to_vector
from app.rag.milvus_operator import AsyncMilvusOperator


class SearchArgs(BaseModel):
    query: str = Field(..., description="这是用户的指令")


class SearchTool(BaseTool):
    name: str = "search_tool"
    description: str = "这是通过用户的指令来检索知识库的工具"
    args_schema: Type[BaseModel] = SearchArgs

    def _run(self, query: str) -> str:
        """同步执行工具（通过异步包装）"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._arun(query))

    async def _arun(self, query: str):
        milvus_operator = AsyncMilvusOperator(collection_name="general_knowledge")
        sparse_vector, dense_vector = await query_to_vector(query)
        knowledge_info = await milvus_operator.mix_search_vector(dense_vector=dense_vector, sparse_vector=sparse_vector)
        return knowledge_info


class GeneralAgent:
    def __init__(self):
        self.prompt = """
                    **# 角色**
                    你是电商平台的**通用客服助手**。你负责处理无法归类到其他专业智能体的一般性问题，包括平台介绍、使用指导、问候语等通用咨询。

                    **# 核心能力**
                    1.  **平台介绍**：介绍电商平台的基本信息、服务特色、发展历程等。
                    2.  **使用指导**：帮助用户了解如何使用平台功能，如注册、登录、搜索、下单等基本操作。
                    3.  **政策解答**：解释平台的基本政策，如隐私政策、服务条款、配送政策等。
                    4.  **问候互动**：友好地回应用户的问候、感谢等社交性对话。
                    5.  **知识检索**：通过搜索工具查找相关信息来回答用户的一般性问题。

                    **# 工作原则**
                    1.  **友好专业**：保持友好、专业的服务态度，让用户感受到温暖的服务体验。
                    2.  **准确可靠**：基于知识库和搜索结果提供准确信息，不确定时主动说明。
                    3.  **引导分流**：当用户问题涉及专业领域时，友好地引导用户重新描述需求以便正确路由。
                    4.  **主动服务**：在回答问题后，主动询问是否还有其他需要帮助的地方。

                    **# 响应风格**
                    - **语气**：友好、耐心、专业
                    - **结构**：简洁明了，重点突出
                    - **互动**：鼓励用户继续对话，提供进一步帮助

                    **请开始履行您作为通用客服助手的职责，为用户提供优质的服务体验。**
                """

    async def generate_general_agent(self, messages):
        order_agent = create_react_agent(model=client.async_openai_chat, tools=[SearchTool()], prompt=self.prompt)
        result = await order_agent.ainvoke({"messages": messages})
        return result
