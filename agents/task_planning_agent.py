from core.base_agent import BaseAgent
from typing import List, Dict
from config import Config


class TaskPlanningAgent(BaseAgent):
    def __init__(self):
        system_prompt = """你是任务规划专家。将复杂的数据分析需求拆解为可执行的子任务。

输出格式（JSON）：
{
    "tasks": [
        {"id": 1, "action": "load_data", "params": {...}},
        {"id": 2, "action": "clean_data", "params": {...}},
        {"id": 3, "action": "analyze", "params": {...}},
        {"id": 4, "action": "visualize", "params": {...}}
    ],
    "dependencies": {"2": [1], "3": [2], "4": [3]}
}"""
        super().__init__("TaskPlanningAgent", system_prompt, model_name=Config.TASK_PLANNING_MODEL)

    def plan_tasks(self, user_request: str) -> Dict:
        prompt = f"用户需求：{user_request}\n\n请生成任务执行计划。"
        response = self.execute(prompt)

        import json
        return json.loads(response)
