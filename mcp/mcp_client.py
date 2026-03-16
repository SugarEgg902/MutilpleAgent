import asyncio
from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass

@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable

class MCPClient:
    """MCP (Model Context Protocol) 客户端，用于调用外部工具"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._initialize_default_tools()

    def _initialize_default_tools(self):
        """初始化默认工具"""
        self.register_tool(
            name="read_file",
            description="读取本地文件内容",
            parameters={
                "file_path": {"type": "string", "description": "文件路径"},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            handler=self._read_file_handler
        )

        self.register_tool(
            name="read_csv",
            description="读取CSV文件并返回数据摘要",
            parameters={
                "file_path": {"type": "string", "description": "CSV文件路径"},
                "max_rows": {"type": "integer", "default": 100}
            },
            handler=self._read_csv_handler
        )

        self.register_tool(
            name="plot_chart",
            description="绘制图表（折线图、柱状图、散点图、饼图等）",
            parameters={
                "chart_type": {"type": "string", "description": "图表类型: line/multi_line/bar/grouped_bar/scatter/pie"},
                "data": {"type": "object", "description": "图表数据"},
                "title": {"type": "string", "default": "Chart"},
                "output_path": {"type": "string", "default": None}
            },
            handler=self._plot_chart_handler
        )

        self.register_tool(
            name="plot_trend",
            description="绘制趋势分析图（从CSV文件）",
            parameters={
                "data_path": {"type": "string", "description": "CSV文件路径"},
                "date_column": {"type": "string", "description": "日期列名"},
                "value_column": {"type": "string", "description": "数值列名"},
                "group_column": {"type": "string", "default": None, "description": "分组列名（可选）"},
                "title": {"type": "string", "default": "趋势分析"},
                "output_path": {"type": "string", "default": None}
            },
            handler=self._plot_trend_handler
        )

        self.register_tool(
            name="web_search",
            description="搜索网络信息",
            parameters={
                "query": {"type": "string", "description": "搜索查询"},
                "max_results": {"type": "integer", "default": 5}
            },
            handler=self._web_search_handler
        )

        self.register_tool(
            name="calculator",
            description="执行数学计算",
            parameters={
                "expression": {"type": "string", "description": "数学表达式"}
            },
            handler=self._calculator_handler
        )

        self.register_tool(
            name="search_amazon",
            description="搜索亚马逊商品信息，返回商品标题、价格、评分等",
            parameters={
                "product_name": {"type": "string", "description": "产品名称/搜索关键词"},
                "max_results": {"type": "integer", "default": 5, "description": "最大返回结果数"}
            },
            handler=self._search_amazon_handler
        )

    def register_tool(self, name: str, description: str,
                     parameters: Dict[str, Any], handler: callable):
        """注册新工具"""
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """异步调用工具"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        tool = self.tools[tool_name]
        try:
            result = await tool.handler(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """获取所有工具的schema"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]

    async def _web_search_handler(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """网络搜索处理器（示例实现）"""
        await asyncio.sleep(0.1)  # 模拟异步操作
        return {
            "query": query,
            "results": [
                {"title": f"Result {i+1}", "url": f"https://example.com/{i+1}"}
                for i in range(max_results)
            ]
        }

    async def _calculator_handler(self, expression: str) -> Dict[str, Any]:
        """计算器处理器"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def _read_file_handler(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """文件读取处理器"""
        try:
            import os
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                "file_path": file_path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}

    async def _read_csv_handler(self, file_path: str, max_rows: int = 100) -> Dict[str, Any]:
        """CSV文件读取处理器"""
        try:
            import pandas as pd
            import os

            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}

            # 尝试多种编码读取
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'iso-8859-1']
            df = None
            used_encoding = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    used_encoding = encoding
                    print(f"[MCP] 成功使用 {encoding} 编码读取文件")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    # 其他错误直接抛出
                    if df is None:
                        raise e

            if df is None:
                return {"error": f"无法读取文件，尝试了以下编码: {', '.join(encodings)}"}

            return {
                "file_path": file_path,
                "encoding": used_encoding,
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "head": df.head(max_rows).to_dict(orient='records'),
                "statistics": df.describe().to_dict(),
                "missing_values": df.isnull().sum().to_dict()
            }
        except Exception as e:
            return {"error": str(e)}

    async def _plot_chart_handler(self, chart_type: str, data: Dict[str, Any],
                                  title: str = "Chart", output_path: str = None) -> Dict[str, Any]:
        """绘图处理器"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # 使用非交互式后端
            import pandas as pd
            import os
            from datetime import datetime

            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False

            # 创建图表目录
            if output_path is None:
                charts_dir = "./charts"
                os.makedirs(charts_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(charts_dir, f"{chart_type}_{timestamp}.png")

            fig, ax = plt.subplots(figsize=(12, 6))

            # 根据图表类型绘制
            if chart_type == "line":
                # 折线图：data = {"x": [...], "y": [...], "label": "..."}
                x_data = data.get("x", [])
                y_data = data.get("y", [])
                label = data.get("label", "Data")
                ax.plot(x_data, y_data, marker='o', label=label, linewidth=2)
                ax.legend()

            elif chart_type == "multi_line":
                # 多条折线：data = {"x": [...], "series": [{"y": [...], "label": "..."}, ...]}
                x_data = data.get("x", [])
                series = data.get("series", [])
                for s in series:
                    ax.plot(x_data, s.get("y", []), marker='o', label=s.get("label", ""), linewidth=2)
                ax.legend()

            elif chart_type == "bar":
                # 柱状图：data = {"x": [...], "y": [...]}
                x_data = data.get("x", [])
                y_data = data.get("y", [])
                ax.bar(x_data, y_data, alpha=0.7)

            elif chart_type == "grouped_bar":
                # 分组柱状图：data = {"x": [...], "series": [{"y": [...], "label": "..."}, ...]}
                x_data = data.get("x", [])
                series = data.get("series", [])
                x_pos = range(len(x_data))
                width = 0.8 / len(series)

                for i, s in enumerate(series):
                    offset = (i - len(series)/2 + 0.5) * width
                    ax.bar([p + offset for p in x_pos], s.get("y", []),
                          width=width, label=s.get("label", ""), alpha=0.7)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(x_data)
                ax.legend()

            elif chart_type == "scatter":
                # 散点图：data = {"x": [...], "y": [...]}
                x_data = data.get("x", [])
                y_data = data.get("y", [])
                ax.scatter(x_data, y_data, alpha=0.6, s=50)

            elif chart_type == "pie":
                # 饼图：data = {"labels": [...], "values": [...]}
                labels = data.get("labels", [])
                values = data.get("values", [])
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')

            else:
                return {"error": f"不支持的图表类型: {chart_type}"}

            # 设置标题和标签
            ax.set_title(title, fontsize=14, fontweight='bold')
            if data.get("xlabel"):
                ax.set_xlabel(data["xlabel"], fontsize=12)
            if data.get("ylabel"):
                ax.set_ylabel(data["ylabel"], fontsize=12)

            # 网格
            if chart_type not in ["pie"]:
                ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return {
                "success": True,
                "output_path": output_path,
                "chart_type": chart_type,
                "title": title
            }

        except Exception as e:
            return {"error": str(e)}

    async def _search_amazon_handler(self, product_name: str, max_results: int = 5) -> Dict[str, Any]:
        """亚马逊商品搜索处理器"""
        try:
            from mcp.search_to_amazon import search_amazon
            products = await asyncio.to_thread(search_amazon, product_name, max_results)
            return {
                "product_name": product_name,
                "total_found": len(products),
                "products": products
            }
        except Exception as e:
            return {"error": str(e)}

    async def _plot_trend_handler(self, data_path: str, date_column: str,
                                  value_column: str, group_column: str = None,
                                  title: str = "趋势分析", output_path: str = None) -> Dict[str, Any]:
        """趋势分析绘图处理器"""
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            import os
            from datetime import datetime

            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False

            # 读取数据
            df = pd.read_csv(data_path)

            # 创建输出路径
            if output_path is None:
                charts_dir = "./charts"
                os.makedirs(charts_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(charts_dir, f"trend_{timestamp}.png")

            fig, ax = plt.subplots(figsize=(14, 7))

            if group_column and group_column in df.columns:
                # 分组趋势图
                for group in df[group_column].unique():
                    group_data = df[df[group_column] == group]
                    ax.plot(group_data[date_column], group_data[value_column],
                           marker='o', label=str(group), linewidth=2)
                ax.legend()
            else:
                # 单一趋势图
                ax.plot(df[date_column], df[value_column],
                       marker='o', linewidth=2, color='#2E86AB')

            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel(date_column, fontsize=12)
            ax.set_ylabel(value_column, fontsize=12)
            ax.grid(True, alpha=0.3)

            # 旋转x轴标签
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return {
                "success": True,
                "output_path": output_path,
                "chart_type": "trend",
                "title": title
            }

        except Exception as e:
            return {"error": str(e)}
