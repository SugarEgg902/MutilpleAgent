from langchain_community.chat_models.tongyi import ChatTongyi
from config import Config
from typing import Dict, Any, Optional
import asyncio
from mcp.mcp_client import MCPClient


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, model_name: str = None):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = ChatTongyi(
            dashscope_api_key=Config.DASHSCOPE_API_KEY,
            model_name=model_name or Config.MODEL
        )
        self.mcp_client: Optional[MCPClient] = None
        print(f"[{self.name}] 初始化，使用模型: {model_name or Config.MODEL}")

    def set_mcp_client(self, mcp_client: MCPClient):
        """设置MCP客户端"""
        self.mcp_client = mcp_client

    def execute(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """同步执行"""
        full_prompt = f"{self.system_prompt}\n\n{user_message}"
        response = self.llm.invoke(full_prompt)
        return response.content

    async def execute_async(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """异步执行，支持MCP工具调用"""
        print(f"[{self.name}] 开始异步执行...")

        full_prompt = f"{self.system_prompt}\n\n{user_message}"

        # 如果有MCP客户端，添加工具信息
        if self.mcp_client:
            tools_schema = self.mcp_client.get_tools_schema()
            full_prompt += f"\n\n可用工具: {tools_schema}"

        # 异步调用LLM - 使用asyncio.to_thread代替run_in_executor
        try:
            print(f"[{self.name}] 正在调用LLM...")
            response = await asyncio.to_thread(self.llm.invoke, full_prompt)
            print(f"[{self.name}] LLM响应完成")
            return response.content
        except Exception as e:
            print(f"[{self.name}] LLM调用失败: {e}")
            # 回退到同步调用
            return self.execute(user_message, context)

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self.mcp_client:
            return {"error": "MCP client not initialized"}

        return await self.mcp_client.call_tool(tool_name, **kwargs)
