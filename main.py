from core.orchestrator import MultiAgentOrchestrator
import asyncio
import os
project_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 60)
    print("多Agent数据分析系统 (支持MCP + 知识库)")
    print("=" * 60)

    orchestrator = MultiAgentOrchestrator()

    # 重建知识库（首次运行或更新知识库时）
    print("\n是否重建知识库? (y/n): ", end="")
    rebuild = input().strip().lower()
    if rebuild == 'y':
        orchestrator.rebuild_knowledge_base()

    # 示例使用
    user_request = "分析销售数据并预测未来3个月的趋势"
    data_path = os.path.join(project_dir, "data", "sales.csv")
    print(data_path)

    print("\n选择运行模式:")
    print("1. 同步模式 (传统)")
    print("2. 异步模式 (支持MCP工具调用)")
    mode = input("请选择 (1/2): ").strip()

    try:
        if mode == "2":
            print("\n[异步模式] 启动...")
            result = asyncio.run(orchestrator.process_request_async(user_request, data_path))
        else:
            print("\n[同步模式] 启动...")

        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
