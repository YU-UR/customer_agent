import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client

from app.core.config import Settings


class MCPOperator:

    def __init__(self):
        settings = Settings()
        self.mcp_server_url = settings.MCP_URL
        self._mcp_session = None
        self._sse_context = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._initialize_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._close_connection()

    async def _initialize_connection(self):
        """初始化MCP连接"""
        try:
            # 创建SSE客户端连接
            self._sse_context = sse_client(self.mcp_server_url)
            streams = await self._sse_context.__aenter__()

            # 创建客户端会话
            self._mcp_session = ClientSession(streams[0], streams[1])
            await self._mcp_session.__aenter__()

            # 初始化会话
            await self._mcp_session.initialize()

            print(f"✅ MCP客户端已连接到: {self.mcp_server_url}")

        except Exception as e:
            print(f"❌ MCP客户端连接失败: {str(e)}")
            await self._close_connection()
            raise

    async def _close_connection(self):
        """关闭连接"""
        if self._mcp_session:
            try:
                await self._mcp_session.__aexit__(None, None, None)
            except:
                pass
            self._mcp_session = None

        if self._sse_context:
            try:
                await self._sse_context.__aexit__(None, None, None)
            except:
                pass
            self._sse_context = None

    async def get_mcp_tools(self, category=None):
        """获取MCP工具列表，可选择按类别筛选"""
        if not self._mcp_session:
            raise Exception("MCP客户端未连接，请使用 async with MCPOperator() 方式")

        try:
            # 获取所有工具
            tools_response = await self._mcp_session.list_tools()
            all_tools = tools_response.tools

            # 如果指定了类别，进行筛选
            if category:
                filtered_tools = []
                for tool in all_tools:
                    # 策略1：名称前缀匹配
                    if tool.name.startswith(f'{category}_'):
                        filtered_tools.append(tool)
                    # 策略2：描述标签匹配
                    elif f'[{category.upper()}]' in tool.description:
                        filtered_tools.append(tool)
                    # 策略3：关键词匹配
                    elif category.lower() in tool.description.lower():
                        filtered_tools.append(tool)

                return filtered_tools

            return all_tools

        except Exception as e:
            print(f"❌ 获取MCP工具失败: {str(e)}")
            return []

    async def call_mcp_tool(self, tool_name, arguments=None):
        """调用MCP工具"""
        if not self._mcp_session:
            raise Exception("MCP客户端未连接，请使用 async with MCPOperator() 方式")

        try:
            # 调用工具
            result = await self._mcp_session.call_tool(
                name=tool_name,
                arguments=arguments or {}
            )

            return {
                "success": True,
                "data": result.content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
