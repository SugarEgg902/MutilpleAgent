from core.base_agent import BaseAgent
import pandas as pd
import json
from typing import Dict, Any, Optional
import asyncio
from config import Config


class DataAnalysisAgent(BaseAgent):
    def __init__(self):
        system_prompt = """你是数据分析专家。你的任务是：
1. 读取和清洗数据
2. 执行统计分析
3. 如果数据中包含产品信息，可以搜索亚马逊热门商品信息作为市场参考
4. 生成可视化图表
5. 提供分析结果的JSON格式输出


可用工具：
- read_csv: 读取CSV文件数据
- calculator: 执行数学计算
- search_amazon: 搜索亚马逊商品信息（参数：product_name, max_results）

工具使用说明：
- 当你需要搜索亚马逊商品信息时，先从数据中识别产品名称
- 然后调用 search_amazon 工具，传入产品名称
- 你可以根据需要多次调用工具

输出格式：
{
    "summary": "数据概览",
    "statistics": {"key": "value"},
    "insights": ["洞察1", "洞察2"],
    "chart_config": {"type": "line/bar/scatter", "data": [...]},
    "amazon_market_info": "亚马逊热门商品总结（如果调用了搜索）"
}"""
        super().__init__("DataAnalysisAgent", system_prompt, model_name=Config.DATA_ANALYSIS_MODEL)
        self.vector_store = None

    def set_vector_store(self, vector_store):
        """设置向量知识库，用于存储Amazon搜索结果"""
        self.vector_store = vector_store

    def analyze_data(self, data_path: str, analysis_request: str) -> Dict[str, Any]:
        """同步分析数据"""
        try:
            df = pd.read_csv(data_path)
            data_info = f"数据形状: {df.shape}\n列名: {df.columns.tolist()}\n前5行:\n{df.head()}"

            prompt = f"""数据信息：
{data_info}

分析任务：
{analysis_request}

请返回 JSON 格式的分析结果"""

            response = self.execute(prompt)
            return json.loads(response)
        except Exception as e:
            return {"error": str(e)}

    async def analyze_data_async(self, data_path: str, analysis_request: str) -> Dict[str, Any]:
        """异步分析数据，让模型自主决定是否调用MCP工具"""
        try:
            # 使用MCP工具读取CSV
            if self.mcp_client:
                print(f"[数据分析] 使用MCP读取CSV: {data_path}")
                csv_result = await self.call_tool("read_csv", file_path=data_path, max_rows=50)
                if csv_result.get("success") and "result" in csv_result:
                    data_info = csv_result["result"]

                    # 构建提示，让模型自己决定是否需要调用Amazon搜索
                    prompt = f"""数据信息：
文件: {data_info.get('file_path')}
形状: {data_info.get('shape')}
列名: {data_info.get('columns')}
数据类型: {data_info.get('dtypes')}
统计摘要: {json.dumps(data_info.get('statistics', {}), ensure_ascii=False)}
缺失值: {data_info.get('missing_values')}
前50行数据: {json.dumps(data_info.get('head', []), ensure_ascii=False)}

分析任务：
{analysis_request}

请分析以上数据：
1. 如果数据中包含产品名称信息，你可以从数据中提取产品名称，然后使用 search_amazon 工具搜索亚马逊市场信息作为参考
2. 完成数据分析后，返回 JSON 格式的分析结果
3. 如果调用了 Amazon 搜索，请在结果中包含 amazon_market_info 字段总结市场情况"""

                    # 让模型自主执行，可能会调用工具
                    response = await self.execute_async(prompt)

                    # 尝试解析JSON
                    try:
                        result = json.loads(response)
                    except:
                        result = {
                            "summary": response,
                            "statistics": data_info.get('statistics', {}),
                            "insights": [],
                            "chart_config": {}
                        }

                    # 确保包含列信息（用于绘图）
                    result["columns"] = data_info.get('columns', [])
                    result["shape"] = data_info.get('shape')
                    result["head"] = data_info.get('head', [])

                    print(f"[数据分析] 分析完成，列名: {result['columns']}")

                    return result
                else:
                    return {"error": f"读取CSV失败: {csv_result.get('error')}"}
            else:
                # 回退到同步方法
                print("[数据分析] MCP客户端未初始化，使用同步方法")
                return self.analyze_data(data_path, analysis_request)

        except Exception as e:
            print(f"[数据分析] 异常: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
