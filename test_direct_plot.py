"""
直接测试绘图功能
"""
import asyncio
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from mcp.mcp_client import MCPClient


async def test_direct_plotting():
    print("=" * 60)
    print("直接测试绘图功能")
    print("=" * 60)

    mcp_client = MCPClient()

    # 测试从CSV绘制趋势图
    csv_path = os.path.join(project_dir, "data", "sales.csv")
    print(f"\nCSV路径: {csv_path}")
    print(f"文件存在: {os.path.exists(csv_path)}")

    print("\n[测试] 绘制趋势图...")
    result = await mcp_client.call_tool(
        "plot_trend",
        data_path=csv_path,
        date_column="date",
        value_column="sales",
        group_column="product",
        title="销售趋势分析"
    )

    print(f"\n结果: {result}")

    if result.get("success"):
        chart_path = result["result"].get("output_path")
        print(f"\n成功！图表已保存: {chart_path}")
        print(f"  文件存在: {os.path.exists(chart_path)}")
    else:
        print(f"\n失败: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_direct_plotting())
