"""
测试多模型配置
验证每个Agent使用的模型是否正确
"""
from core.orchestrator import MultiAgentOrchestrator
from config import Config


def test_model_configuration():
    print("=" * 60)
    print("多模型配置测试")
    print("=" * 60)

    print("\n[配置信息]")
    print(f"默认模型: {Config.MODEL}")
    print(f"高级模型: {Config.ORCHESTRA_MODEL}")
    print(f"任务规划模型: {Config.TASK_PLANNING_MODEL}")
    print(f"数据分析模型: {Config.DATA_ANALYSIS_MODEL}")
    print(f"报告生成模型: {Config.REPORT_GENERATION_MODEL}")
    print(f"质量控制模型: {Config.QUALITY_CONTROL_MODEL}")

    print("\n[初始化Orchestrator]")
    orchestrator = MultiAgentOrchestrator()

    print("\n[验证Agent模型配置]")
    agents = [
        ("任务规划Agent", orchestrator.task_planner, Config.TASK_PLANNING_MODEL),
        ("数据分析Agent", orchestrator.data_analyst, Config.DATA_ANALYSIS_MODEL),
        ("报告生成Agent", orchestrator.report_generator, Config.REPORT_GENERATION_MODEL),
        ("质量控制Agent", orchestrator.quality_controller, Config.QUALITY_CONTROL_MODEL),
    ]

    all_correct = True
    for name, agent, expected_model in agents:
        actual_model = agent.llm.model_name
        status = "✓" if actual_model == expected_model else "✗"
        print(f"{status} {name}: {actual_model} (期望: {expected_model})")

        if actual_model != expected_model:
            all_correct = False

    print("\n" + "=" * 60)
    if all_correct:
        print("✓ 所有Agent模型配置正确！")
        print("\n[重点] 质量控制Agent使用更强模型: " + Config.QUALITY_CONTROL_MODEL)
    else:
        print("✗ 部分Agent模型配置不正确，请检查")

    print("=" * 60)


if __name__ == "__main__":
    test_model_configuration()
