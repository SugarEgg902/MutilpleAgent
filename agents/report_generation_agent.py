from core.base_agent import BaseAgent
from typing import Dict, Any
import json
import asyncio
from config import Config


class ReportGenerationAgent(BaseAgent):
    def __init__(self):
        system_prompt = """你是报告生成专家。基于分析结果、图表和统计数据生成结构化报告。

报告结构：
1. 执行摘要
2. 数据概览
3. 关键发现
4. 趋势分析
5. 洞察与结论
6. 行动建议

输出Markdown格式的专业报告。"""
        super().__init__("ReportGenerationAgent", system_prompt, model_name=Config.REPORT_GENERATION_MODEL)

    def generate_report(self, analysis_result: Dict[str, Any],
                       chart_data: Dict[str, Any],
                       statistics: Dict[str, Any]) -> str:
        prompt = f"""请基于以下信息生成数据分析报告：

分析结果：
{analysis_result}

图表数据：
{chart_data}

统计数据：
{statistics}

生成完整的Markdown格式报告。"""

        return self.execute(prompt)

    async def generate_report_with_charts(self, analysis_result: Dict[str, Any],
                                         data_path: str = None) -> Dict[str, Any]:
        """生成报告并自动绘制图表"""
        try:
            # 1. 生成报告文本
            prompt = f"""请基于以下分析结果生成数据分析报告：

分析结果：
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

生成完整的Markdown格式报告。"""

            report_text = await self.execute_async(prompt)

            # 2. 提取图表配置
            chart_config = analysis_result.get("chart_config", {})
            chart_paths = []

            print(f"\n[绘图检查] MCP客户端: {self.mcp_client is not None}")
            print(f"[绘图检查] 数据路径: {data_path}")
            print(f"[绘图检查] 图表配置: {chart_config}")

            # 3. 如果有数据路径和数据，尝试绘制图表
            if self.mcp_client and data_path and "head" in analysis_result:
                print("\n[绘图] 开始绘图流程...")

                # 获取数据
                data_rows = analysis_result.get("head", [])
                columns = analysis_result.get("columns", [])

                print(f"[绘图] 数据行数: {len(data_rows)}, 列名: {columns}")

                if data_rows and columns:
                    # 智能推断列类型
                    date_col = None
                    value_col = None
                    category_col = None

                    for col in columns:
                        col_lower = str(col).lower()
                        if any(x in col_lower for x in ["date", "time", "日期", "时间", "month", "year"]):
                            date_col = col
                        elif any(x in col_lower for x in ["sales", "amount", "value", "revenue", "销售", "金额", "数值", "收入"]):
                            if value_col is None:  # 只取第一个数值列
                                value_col = col
                        elif any(x in col_lower for x in ["product", "region", "category", "name", "产品", "地区", "类别", "名称"]):
                            if category_col is None:  # 只取第一个分类列
                                category_col = col

                    print(f"[绘图] 推断列名 - 日期: {date_col}, 数值: {value_col}, 分类: {category_col}")

                    # 场景1: 有日期列 - 绘制趋势图
                    if date_col and value_col:
                        print(f"\n[绘图] 场景1: 绘制时间趋势图...")
                        try:
                            trend_result = await self.call_tool(
                                "plot_trend",
                                data_path=data_path,
                                date_column=date_col,
                                value_column=value_col,
                                group_column=category_col,
                                title=f"{value_col} 趋势分析"
                            )

                            if trend_result.get("success") and "result" in trend_result:
                                chart_path = trend_result["result"].get("output_path")
                                if chart_path:
                                    chart_paths.append(chart_path)
                                    print(f"[绘图] ✓ 趋势图已保存: {chart_path}")
                        except Exception as e:
                            print(f"[绘图] 趋势图失败: {e}")

                    # 场景2: 有分类列和数值列 - 绘制柱状图
                    if category_col and value_col and len(data_rows) <= 20:
                        print(f"\n[绘图] 场景2: 绘制分类柱状图...")
                        try:
                            # 提取数据
                            categories = [str(row.get(category_col, "")) for row in data_rows[:20]]
                            values = [float(row.get(value_col, 0)) for row in data_rows[:20]]

                            chart_data = {
                                "x": categories,
                                "y": values,
                                "xlabel": category_col,
                                "ylabel": value_col
                            }

                            bar_result = await self.call_tool(
                                "plot_chart",
                                chart_type="bar",
                                data=chart_data,
                                title=f"{category_col} vs {value_col}"
                            )

                            if bar_result.get("success") and "result" in bar_result:
                                chart_path = bar_result["result"].get("output_path")
                                if chart_path:
                                    chart_paths.append(chart_path)
                                    print(f"[绘图] ✓ 柱状图已保存: {chart_path}")
                        except Exception as e:
                            print(f"[绘图] 柱状图失败: {e}")

                    # 场景3: 使用 chart_config 中的配置
                    if chart_config.get("type") and chart_config.get("data"):
                        print(f"\n[绘图] 场景3: 使用 chart_config 绘图...")
                        try:
                            plot_result = await self.call_tool(
                                "plot_chart",
                                chart_type=chart_config["type"],
                                data=chart_config["data"],
                                title=chart_config.get("title", "数据分析图表")
                            )

                            if plot_result.get("success") and "result" in plot_result:
                                chart_path = plot_result["result"].get("output_path")
                                if chart_path:
                                    chart_paths.append(chart_path)
                                    print(f"[绘图] ✓ 自定义图表已保存: {chart_path}")
                        except Exception as e:
                            print(f"[绘图] 自定义图表失败: {e}")

            else:
                if not self.mcp_client:
                    print("[绘图] 跳过：MCP客户端未初始化")
                if not data_path:
                    print("[绘图] 跳过：未提供数据路径")
                if "head" not in analysis_result:
                    print("[绘图] 跳过：分析结果中没有数据")

            # 4. 在报告中添加图表引用
            if chart_paths:
                chart_section = "\n\n## 可视化图表\n\n"
                for i, path in enumerate(chart_paths, 1):
                    chart_section += f"{i}. 图表已保存至: `{path}`\n"

                report_text += chart_section

            return {
                "report": report_text,
                "chart_paths": chart_paths,
                "chart_count": len(chart_paths)
            }

        except Exception as e:
            print(f"[绘图] 异常: {e}")
            import traceback
            traceback.print_exc()

            return {
                "report": f"报告生成失败: {str(e)}",
                "chart_paths": [],
                "chart_count": 0,
                "error": str(e)
            }
