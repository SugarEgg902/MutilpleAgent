from core.orchestrator import MultiAgentOrchestrator
import asyncio
import os


async def test_async_mode():
    print("=" * 60)
    print("异步模式调试测试")
    print("=" * 60)

    orchestrator = MultiAgentOrchestrator()

    # 测试请求
    user_request = "分析销售数据并预测未来3个月的趋势"
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_dir, "data", "sales.csv")

    print(f"\n用户请求: {user_request}")
    print(f"数据路径: {data_path}")
    print(f"文件存在: {os.path.exists(data_path)}")

    try:
        print("\n开始异步处理...")
        result = await orchestrator.process_request_async(user_request, data_path)

        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"会话ID: {result['session_id']}")
        print(f"知识库检索: {len(result.get('kb_context', []))} 条")
        print(f"图表数量: {len(result.get('chart_paths', []))}")

        if result.get('chart_paths'):
            print("\n生成的图表:")
            for path in result['chart_paths']:
                print(f"  - {path}")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_async_mode())
