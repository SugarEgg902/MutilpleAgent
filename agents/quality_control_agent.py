from core.base_agent import BaseAgent
from typing import Dict, Any
from config import Config


class QualityControlAgent(BaseAgent):
    def __init__(self):
        system_prompt = """你是质量控制专家。检查数据分析的合理性和准确性。

检查项：
1. 分析方法是否合理
2. 数据是否存在异常
3. 结论逻辑是否严密
4. 统计显著性

输出格式（JSON）：
{
    "credibility_score": 0.85,
    "issues": [
        {"type": "data_anomaly", "severity": "medium", "description": "..."}
    ],
    "corrections": ["建议1", "建议2"],
    "approved": true/false
}"""
        # 使用更强大的模型进行质量控制
        super().__init__("QualityControlAgent", system_prompt, model_name=Config.QUALITY_CONTROL_MODEL)

    def validate(self, analysis_result: Dict[str, Any],
                report: str) -> Dict[str, Any]:
        prompt = f"""请检查以下分析结果和报告的质量：

分析结果：
{analysis_result}

报告内容：
{report}

返回质量评估JSON。"""

        import json
        response = self.execute(prompt)
        return json.loads(response)
