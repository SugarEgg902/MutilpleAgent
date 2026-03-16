"""
MCP工具使用示例
演示如何注册和使用自定义MCP工具
"""
import asyncio
from mcp.mcp_client import MCPClient


async def custom_data_processor(data: str, operation: str) -> dict:
    """自定义数据处理工具"""
    await asyncio.sleep(0.1)

    operations = {
        "uppercase": data.upper(),
        "lowercase": data.lower(),
        "reverse": data[::-1],
        "length": len(data)
    }

    return {
        "operation": operation,
        "input": data,
        "result": operations.get(operation, "Unknown operation")
    }


async def main():
    # 初始化MCP客户端
    mcp_client = MCPClient()

    # 注册自定义工具
    mcp_client.register_tool(
        name="data_processor",
        description="处理文本数据",
        parameters={
            "data": {"type": "string", "description": "输入数据"},
            "operation": {"type": "string", "description": "操作类型: uppercase/lowercase/reverse/length"}
        },
        handler=custom_data_processor
    )

    # 测试内置工具
    print("=== 测试计算器工具 ===")
    calc_result = await mcp_client.call_tool("calculator", expression="2 + 3 * 4")
    print(f"结果: {calc_result}")

    print("\n=== 测试网络搜索工具 ===")
    search_result = await mcp_client.call_tool("web_search", query="Python数据分析", max_results=3)
    print(f"结果: {search_result}")

    print("\n=== 测试自定义工具 ===")
    custom_result = await mcp_client.call_tool("data_processor", data="Hello World", operation="uppercase")
    print(f"结果: {custom_result}")

    # 获取所有工具schema
    print("\n=== 所有可用工具 ===")
    tools = mcp_client.get_tools_schema()
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")


if __name__ == "__main__":
    asyncio.run(main())
