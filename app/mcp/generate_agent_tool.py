import asyncio
from typing import Dict, Optional

from langchain_core.tools import BaseTool
from pydantic import Field

from .mcp_operator import MCPOperator


class MCPTool(BaseTool):
    """MCP工具包装器，将MCP工具转换为LangChain工具"""

    name: str = Field(description="工具名称")
    description: str = Field(description="工具描述")
    tool_schema: Optional[Dict] = Field(default=None, description="工具参数schema")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, name: str, description: str, tool_schema=None, **kwargs):
        super().__init__(name=name, description=description, tool_schema=tool_schema, **kwargs)

        # 如果有schema，更新工具描述以包含参数信息
        if tool_schema and isinstance(tool_schema, dict):
            if 'properties' in tool_schema:
                param_info = []
                for param_name, param_def in tool_schema['properties'].items():
                    param_desc = param_def.get('description', param_name)
                    param_type = param_def.get('type', 'any')
                    param_info.append(f"{param_name}({param_type}): {param_desc}")

                if param_info:
                    self.description += f"\n参数: {', '.join(param_info)}"

    def _run(self, **kwargs) -> str:
        """同步执行工具（通过异步包装）"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._arun(**kwargs))

    async def _arun(self, **kwargs) -> str:
        """异步执行MCP工具"""
        # 处理参数映射
        processed_args = kwargs.get("kwargs", kwargs)

        async with MCPOperator() as mcp_operator:
            result = await mcp_operator.call_mcp_tool(self.name, processed_args)

            # 处理返回结果
            if result.get("success", False):
                data = result.get("data", [])
                if isinstance(data, list) and len(data) > 0:
                    content = data[0]
                    if hasattr(content, 'text'):
                        return content.text
                    else:
                        return str(content)
                else:
                    return str(data) if data else "工具执行成功，但没有返回内容"
            else:
                error_msg = result.get("error", "未知错误")
                return f"工具调用失败: {error_msg}"
