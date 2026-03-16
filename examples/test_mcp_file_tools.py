"""
测试MCP文件读取工具
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from mcp.mcp_client import MCPClient


async def test_file_tools():
    mcp_client = MCPClient()

    # 测试读取CSV
    print("=== 测试CSV读取 ===")
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_dir, "data", "sales.csv")

    result = await mcp_client.call_tool("read_csv", file_path=csv_path, max_rows=10)
    print(f"完整结果: {result}")

    if result.get("success"):
        data = result.get("result", {})
        print(f"文件: {data.get('file_path', 'N/A')}")
        print(f"形状: {data.get('shape', 'N/A')}")
        print(f"列名: {data.get('columns', [])}")
        print(f"数据类型: {data.get('dtypes', {})}")
        print(f"缺失值: {data.get('missing_values', {})}")
        print(f"\n前10行:")
        for i, row in enumerate(data.get('head', [])[:5], 1):
            print(f"  {i}. {row}")
    else:
        print(f"错误: {result.get('error')}")

    # 测试读取文本文件
    print("\n=== 测试文本文件读取 ===")
    txt_path = os.path.join(project_dir, "knowledgeBase", "domain_knowledge.txt")

    result = await mcp_client.call_tool("read_file", file_path=txt_path)

    if result.get("success"):
        data = result.get("result", {})
        print(f"文件: {data.get('file_path', 'N/A')}")
        print(f"大小: {data.get('size', 0)} 字符")
        content = data.get('content', '')
        print(f"内容预览:\n{content[:200]}...")
    else:
        print(f"错误: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_file_tools())
