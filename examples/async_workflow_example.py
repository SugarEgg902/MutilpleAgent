"""
完整异步流程示例
演示MCP + 知识库的集成使用
"""
import asyncio
from core.orchestrator import MultiAgentOrchestrator


async def main():
    print("=" * 60)
    print("异步多Agent系统演示")
    print("=" * 60)

    # 初始化编排器
    orchestrator = MultiAgentOrchestrator()

    # 重建知识库
    print("\n[1] 重建知识库...")
    kb_stats = orchestrator.rebuild_knowledge_base()
    print(f"知识库统计: {kb_stats}")

    # 测试请求
    test_requests = [
        "分析销售数据的趋势和季节性",
        "如何处理数据中的缺失值？",
        "预测未来3个月的销售额"
    ]

    for i, request in enumerate(test_requests, 1):
        print(f"\n{'=' * 60}")
        print(f"[{i}] 处理请求: {request}")
        print('=' * 60)

        try:
            result = await orchestrator.process_request_async(
                user_request=request,
                data_path="data/sales.csv"
            )

            print(f"\n会话ID: {result['session_id']}")
            print(f"知识库检索: {len(result['kb_context'])} 条相关知识")
            print(f"质量评分: {result['quality'].get('credibility_score', 'N/A')}")

        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
