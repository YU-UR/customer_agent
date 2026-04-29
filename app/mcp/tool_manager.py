"""
MCP工具管理器
负责管理和协调所有MCP工具的生命周期
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from .mcp_operator import MCPOperator
from app.core.config import settings
from .generate_agent_tool import MCPTool

logger = logging.getLogger(__name__)


class MCPToolManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tools_by_category: Dict[str, List[MCPTool]] = {}
        self.mcp_servers: List[str] = []
        self.is_initialized = False
        
    async def initialize(self):
        """初始化工具管理器"""
        if self.is_initialized:
            return
            
        try:
            logger.info("正在初始化MCP工具管理器...")
            await self._load_mcp_tools()
            self.is_initialized = True
            logger.info("MCP工具管理器初始化完成")
        except Exception as e:
            logger.error(f"MCP工具管理器初始化失败: {e}")
            raise
    
    async def _load_mcp_tools(self):
        """加载MCP工具"""
        try:
            async with MCPOperator() as mcp_operator:
                # 获取所有可用工具
                all_tools = await mcp_operator.get_mcp_tools()
                
                for tool in all_tools:
                    # 解析工具分类（从描述中提取）
                    category = self._extract_category_from_description(tool.description)
                    
                    # 创建MCPTool实例
                    mcp_tool = MCPTool(
                        name=tool.name,
                        description=tool.description,
                        tool_schema=getattr(tool, 'inputSchema', None)
                    )
                    
                    # 添加到工具字典
                    self.tools[tool.name] = mcp_tool
                    
                    # 按分类组织工具
                    if category not in self.tools_by_category:
                        self.tools_by_category[category] = []
                    self.tools_by_category[category].append(mcp_tool)
                    
                logger.info(f"成功加载 {len(self.tools)} 个MCP工具")
                
        except Exception as e:
            logger.error(f"加载MCP工具失败: {e}")
            raise
    
    def _extract_category_from_description(self, description: str) -> str:
        """从工具描述中提取分类"""
        if not description:
            return "SYSTEM"
            
        # 从描述中提取分类标签，格式如 [order]、[product] 等
        if description.startswith('[') and ']' in description:
            category_end = description.find(']')
            category = description[1:category_end].upper()
            
            # 映射到标准分类
            category_mapping = {
                'ORDER': 'ORDER',
                'PRODUCT': 'PRODUCT', 
                'SALES': 'AFTER_SALES',
                'AFTER_SALES': 'AFTER_SALES',
                'PROMOTION': 'PROMOTION',
                'SYSTEM': 'SYSTEM'
            }
            
            return category_mapping.get(category, 'SYSTEM')
        
        return 'SYSTEM'
    
    async def add_mcp_server(self, server_url: str):
        """添加MCP服务器"""
        if server_url not in self.mcp_servers:
            self.mcp_servers.append(server_url)
            logger.info(f"添加MCP服务器: {server_url}")
    
    def get_all_tools(self) -> List[MCPTool]:
        """获取所有工具"""
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[MCPTool]:
        """根据分类获取工具"""
        return self.tools_by_category.get(category.upper(), [])
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPTool]:
        """根据名称获取工具"""
        return self.tools.get(tool_name)
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用指定工具"""
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        try:
            result = await tool._arun(**kwargs)
            return result
        except Exception as e:
            logger.error(f"调用工具 '{tool_name}' 失败: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            async with MCPOperator() as mcp_operator:
                # 尝试获取工具列表来检查连接
                tools = await mcp_operator.get_mcp_tools()
                
                return {
                    "status": "healthy",
                    "tools_count": len(tools),
                    "categories": list(self.tools_by_category.keys()),
                    "servers": self.mcp_servers,
                    "initialized": self.is_initialized
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self.is_initialized
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        categories = {}
        for category, tools in self.tools_by_category.items():
            categories[category] = {
                "count": len(tools),
                "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
            }
        
        return {
            "total_tools": len(self.tools),
            "categories": categories,
            "servers": self.mcp_servers,
            "initialized": self.is_initialized
        }
    
    async def close_all(self):
        """关闭所有连接"""
        logger.info("正在关闭MCP工具管理器...")
        self.tools.clear()
        self.tools_by_category.clear()
        self.mcp_servers.clear()
        self.is_initialized = False
        logger.info("MCP工具管理器已关闭")


# 全局工具管理器实例
tool_manager = MCPToolManager()


@asynccontextmanager
async def get_tool_manager():
    """获取工具管理器的异步上下文管理器"""
    if not tool_manager.is_initialized:
        await tool_manager.initialize()
    yield tool_manager


# 便捷函数
async def initialize_tools():
    """初始化工具"""
    await tool_manager.initialize()
    # 使用配置中的 MCP_URL
    if settings.MCP_URL:
        await tool_manager.add_mcp_server(settings.MCP_URL)


async def cleanup_tools():
    """清理工具"""
    await tool_manager.close_all()


async def get_available_tools(category: Optional[str] = None) -> List[MCPTool]:
    """获取可用工具"""
    if not tool_manager.is_initialized:
        await tool_manager.initialize()
    
    if category:
        return tool_manager.get_tools_by_category(category)
    return tool_manager.get_all_tools()


async def call_tool(tool_name: str, **kwargs) -> Any:
    """调用工具"""
    return await tool_manager.call_tool(tool_name, **kwargs)


def get_tools_info() -> Dict[str, Any]:
    """获取工具信息"""
    return tool_manager.get_tool_info()