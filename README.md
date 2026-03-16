# 🤖 多智能体数据分析系统

<div align="center">

**基于 MCP 协议的智能数据分析平台 | 支持质量重试 | Web 可视化界面**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#-快速开始) • [核心特性](#-核心特性) • [系统架构](#-系统架构) • [Web界面](#-web-界面) • [文档](#-详细文档)

</div>

---

## ✨ 核心特性

### 🎯 智能多 Agent 协作
- **4 个专业 Agent**：任务规划、数据分析、报告生成、质量控制
- **自动质量重试**：质量不合格时自动重新分析，最多重试 2 次
- **智能工具调用**：模型自主决定何时调用 Amazon 搜索等外部工具
- **异步并发处理**：支持高效的异步工作流，提升处理速度

### 🛠️ MCP 工具生态
- **7+ 内置工具**：CSV 读取、图表绘制、Amazon 商品搜索、计算器等
- **自动编码检测**：支持 UTF-8、GBK、GB2312 等多种编码格式
- **智能图表生成**：自动识别数据类型，生成趋势图、柱状图、散点图等
- **可扩展架构**：轻松注册自定义工具

### 📚 RAG 知识库系统
- **智能去重**：基于 MD5 哈希的文档查重机制
- **语义检索**：ChromaDB 向量数据库支持
- **多格式支持**：TXT、Markdown、JSON 文档自动加载
- **增量更新**：只处理新增或修改的文档

### 🌐 现代化 Web 界面
- **文件上传**：支持知识库文件和销售数据上传
- **实时分析**：在线提问，实时查看分析结果
- **历史记录**：查看所有历史分析会话
- **图表展示**：自动显示生成的可视化图表
- **响应式设计**：美观的渐变 UI，支持移动端

### 🔄 质量保障机制
- **自动质量评估**：每次分析后自动进行质量检查
- **智能重试**：质量不合格时带反馈重新分析
- **可信度评分**：0-1 分数评估分析可靠性
- **问题追踪**：详细记录发现的问题和改进建议

---

## 🚀 快速开始

### 1. 安装依赖
```bash
git clone <repository-url>
cd MutilpleAgent
pip install -r requirements.txt
```

### 2. 配置环境
编辑 `config.py`：
```python
class Config:
    DASHSCOPE_API_KEY = "your-api-key"  # 阿里云 DashScope API Key

    # 模型配置（可按需调整）
    TASK_PLANNING_MODEL = "qwen-turbo"      # 任务规划
    DATA_ANALYSIS_MODEL = "qwen3-max"       # 数据分析
    REPORT_GENERATION_MODEL = "qwen3-max"   # 报告生成
    QUALITY_CONTROL_MODEL = "qwen3.5-plus"  # 质量控制（推荐强模型）
```

### 3. 启动 Web 服务
```bash
python web_app.py
```

访问 http://localhost:8000 开始使用！

### 4. 使用 Web 界面
1. **上传知识库文件**：点击左侧"上传知识库"按钮
2. **上传销售数据**：上传 CSV 格式的销售数据
3. **提出问题**：在底部输入框输入问题，如"分析当前销售数据"
4. **查看结果**：系统自动分析并展示报告、图表、质量评估

---

## 🏗️ 系统架构

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                      Web 界面 (FastAPI)                  │
│  文件上传 | 实时分析 | 历史记录 | 图表展示                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Orchestrator (编排器)                   │
│  • 异步工作流  • 质量重试  • 超时控制                    │
└─────┬──────┬──────┬──────┬──────────────────────────────┘
      │      │      │      │
┌─────▼──┐ ┌─▼────┐ ┌▼────┐ ┌▼──────────┐
│ 任务   │ │ 数据 │ │报告 │ │ 质量      │
│ 规划   │ │ 分析 │ │生成 │ │ 控制      │
│ Agent  │ │Agent │ │Agent│ │ Agent     │
└────────┘ └──┬───┘ └─────┘ └───────────┘
              │
         ┌────▼─────┐
         │   MCP    │
         │  工具层  │
         └──────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼───┐  ┌─▼────┐
│ CSV  │  │ 绘图 │  │Amazon│
│ 读取 │  │ 工具 │  │ 搜索 │
└──────┘  └──────┘  └──────┘
```

### 4 个核心 Agent

| Agent | 模型 | 职责 |
|-------|------|------|
| **TaskPlanningAgent** | qwen-turbo | 拆解复杂需求，生成执行计划 |
| **DataAnalysisAgent** | qwen3-max | 数据读取、统计分析、工具调用 |
| **ReportGenerationAgent** | qwen3-max | 生成 Markdown 报告、自动绘图 |
| **QualityControlAgent** | qwen3.5-plus | 质量评估、可信度评分、重试决策 |

### 存储层

- **Redis**：短期记忆存储（会话、中间结果）
- **ChromaDB**：向量检索增强（历史分析、知识库）
- **本地文件**：图表、MD5 哈希记录

---

## 🌐 Web 界面

### 主要功能

#### 📤 文件管理
- **知识库上传**：支持 .md、.txt、.pdf 格式
- **数据上传**：支持 CSV 格式销售数据
- **自动索引**：上传后自动重建知识库索引

#### 💬 智能对话
- **自然语言提问**：如"分析当前销售数据的趋势"
- **自动文件选择**：未指定文件时自动使用 data 目录下的 CSV
- **实时反馈**：显示分析进度和状态

#### 📊 结果展示
- **分析摘要**：数据概览和关键统计
- **关键洞察**：自动提取的业务洞察
- **质量评估**：可信度评分、问题列表、改进建议
- **可视化图表**：自动生成的趋势图、柱状图等
- **重试标记**：显示是否经过质量重试

#### 📜 历史记录
- **会话管理**：保存最近 50 条分析记录
- **一键回顾**：点击"查看历史记录"快速浏览
- **完整上下文**：包含问题、结果、图表路径

---

## 🎨 核心亮点详解

### 1. 质量重试机制

系统在质量评估不通过时自动重试，确保分析质量：

```python
# 质量评估流程
while retry_count <= max_retries:
    quality_check = await quality_controller.evaluate(analysis, report)

    if not quality_check["approved"] and retry_count < max_retries:
        # 提取问题和建议
        issues = quality_check["issues"]
        corrections = quality_check["corrections"]

        # 带反馈重新分析
        analysis = await data_analyst.analyze(
            data_path,
            user_request + f"\n质量反馈: {issues}\n改进建议: {corrections}"
        )

        # 重新生成报告
        report = await report_generator.generate(analysis)
        retry_count += 1
    else:
        break
```

**效果**：
- ✅ 自动发现分析中的问题
- ✅ 针对性改进分析方法
- ✅ 最多重试 2 次，避免无限循环
- ✅ 记录重试次数，便于追踪

### 2. 智能工具调用

模型自主决定何时调用外部工具，而非硬编码：

```python
# 数据分析 Agent 的 System Prompt
"""
可用工具：
- search_amazon: 搜索亚马逊商品信息（参数：product_name, max_results）

工具使用说明：
- 当你需要搜索亚马逊商品信息时，先从数据中识别产品名称
- 然后调用 search_amazon 工具，传入产品名称
- 你可以根据需要多次调用工具
"""
```

**优势**：
- 🧠 模型自主判断是否需要外部信息
- 🎯 从数据中智能提取产品名称
- 🔄 支持多次工具调用
- 📊 工具结果自动融入分析

### 3. 自动编码检测

支持多种 CSV 编码格式，无需手动指定：

```python
encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'iso-8859-1']
for encoding in encodings:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        print(f"成功使用 {encoding} 编码读取文件")
        break
    except UnicodeDecodeError:
        continue
```

**支持编码**：UTF-8、GBK、GB2312、GB18030、Latin1、ISO-8859-1

### 4. 智能图表生成

自动识别数据类型并生成合适的图表：

```python
# 场景 1: 有日期列 → 时间趋势图
if date_col and value_col:
    plot_trend(date_column=date_col, value_column=value_col, group_column=category_col)

# 场景 2: 有分类列 → 柱状图
if category_col and value_col:
    plot_chart(chart_type="bar", data={"x": categories, "y": values})

# 场景 3: 使用模型提供的配置
if chart_config:
    plot_chart(chart_type=chart_config["type"], data=chart_config["data"])
```

**智能推断**：
- 📅 日期列：包含 date/time/日期/时间
- 💰 数值列：包含 sales/amount/revenue/销售/金额
- 🏷️ 分类列：包含 product/region/category/产品/地区

### 5. MD5 去重机制

避免重复处理相同的文档内容：

```
文档 → 分割成 chunks → 计算 MD5 → 检查 ./MD5/ 目录
                                    ↓
                        存在 → 跳过（去重）
                        不存在 → 存储到向量库 + 保存 MD5
```

**优势**：
- ⚡ 增量更新，只处理新内容
- 💾 节省存储空间
- 🔍 快速查重，基于哈希比对

---

## 📖 详细文档

### MCP 工具系统

#### 内置工具列表

| 工具名 | 描述 | 主要参数 |
|--------|------|----------|
| `read_csv` | 读取 CSV 文件并返回数据摘要 | file_path, max_rows |
| `plot_chart` | 绘制图表（折线/柱状/散点/饼图） | chart_type, data, title |
| `plot_trend` | 从 CSV 绘制趋势分析图 | data_path, date_column, value_column |
| `search_amazon` | 搜索亚马逊商品信息 | product_name, max_results |
| `calculator` | 执行数学计算 | expression |
| `read_file` | 读取本地文件内容 | file_path, encoding |
| `web_search` | 搜索网络信息（示例） | query, max_results |

#### 注册自定义工具

```python
from mcp.mcp_client import MCPClient

async def my_custom_tool(param1: str, param2: int) -> dict:
    # 工具逻辑
    return {"result": "success"}

mcp_client = MCPClient()
mcp_client.register_tool(
    name="my_tool",
    description="工具描述",
    parameters={
        "param1": {"type": "string", "description": "参数1"},
        "param2": {"type": "integer", "default": 10}
    },
    handler=my_custom_tool
)
```

### 知识库系统

#### 文档加载流程

1. 扫描 `./knowledgeBase/` 目录
2. 使用语义分割器切分文档（chunk_size=500, overlap=50）
3. 计算每个 chunk 的 MD5 哈希
4. 查重：检查 `./MD5/` 目录
5. 存储新 chunk 到 ChromaDB

#### 语义搜索

```python
from knowledge.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
results = kb.search("如何处理缺失数据？", n_results=5)

for result in results:
    print(f"内容: {result['content']}")
    print(f"来源: {result['metadata']['source']}")
```

### 模型配置建议

#### 平衡方案（推荐）
```python
TASK_PLANNING_MODEL = "qwen-turbo"      # 快速规划
DATA_ANALYSIS_MODEL = "qwen3-max"       # 准确分析
REPORT_GENERATION_MODEL = "qwen3-max"   # 流畅表达
QUALITY_CONTROL_MODEL = "qwen3.5-plus"  # 强力质检
```
**成本**：约 ¥0.08/请求

#### 性能优先
```python
# 全部使用 qwen3.5-plus
```
**成本**：约 ¥0.20/请求

#### 成本优先
```python
# 全部使用 qwen-turbo
```
**成本**：约 ¥0.03/请求

---

## 🔧 API 使用

### 异步工作流（推荐）

```python
import asyncio
from core.orchestrator import MultiAgentOrchestrator

async def main():
    orchestrator = MultiAgentOrchestrator()

    # 首次运行：重建知识库
    orchestrator.rebuild_knowledge_base()

    # 异步处理请求
    result = await orchestrator.process_request_async(
        user_request="分析销售数据并预测趋势",
        data_path="E:/agent/MutilpleAgent/data/sales.csv"
    )

    print(f"会话ID: {result['session_id']}")
    print(f"重试次数: {result['retry_count']}")
    print(f"质量通过: {result['quality']['approved']}")
    print(f"图表: {result['chart_paths']}")

asyncio.run(main())
```

### Web API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 返回 Web 界面 |
| `/upload/knowledge` | POST | 上传知识库文件 |
| `/upload/data` | POST | 上传销售数据 |
| `/query` | POST | 提交分析请求 |
| `/history` | GET | 获取历史记录 |
| `/files/data` | GET | 列出数据文件 |
| `/files/knowledge` | GET | 列出知识库文件 |
| `/charts/{filename}` | GET | 获取图表文件 |

---

## 📁 项目结构

```
MutilpleAgent/
├── agents/                      # Agent 实现
│   ├── task_planning_agent.py
│   ├── data_analysis_agent.py
│   ├── report_generation_agent.py
│   └── quality_control_agent.py
├── core/                        # 核心模块
│   ├── base_agent.py           # Agent 基类（支持 MCP）
│   └── orchestrator.py         # 编排器（异步 + 质量重试）
├── mcp/                         # MCP 客户端
│   ├── mcp_client.py           # 工具管理
│   └── search_to_amazon.py     # Amazon 搜索
├── knowledge/                   # 知识库系统
│   └── knowledge_base.py       # 文档加载、分割、查重
├── storage/                     # 存储层
│   ├── redis_memory.py         # Redis 短期记忆
│   └── chroma_store.py         # 向量存储
├── templates/                   # Web 模板
│   └── index.html              # 前端界面
├── knowledgeBase/               # 知识文档目录
├── data/                        # 数据文件目录
├── charts/                      # 生成的图表
├── MD5/                         # MD5 哈希记录
├── chroma_kb/                   # 知识库向量存储
├── web_app.py                   # Web 服务器
├── config.py                    # 配置文件
└── requirements.txt             # 依赖列表
```

---

## 🐛 故障排查

### 图表内容为空
**原因**：数据未正确传递给绘图工具
**解决**：
1. 检查 CSV 文件编码（系统会自动尝试多种编码）
2. 确认数据列名能被正确识别
3. 查看控制台日志中的 `[绘图]` 信息

### 质量检查总是通过
**原因**：质量控制模型不够强
**解决**：在 `config.py` 中设置 `QUALITY_CONTROL_MODEL = "qwen3.5-plus"`

### Web 界面无法访问
**原因**：端口被占用
**解决**：修改 `web_app.py` 中的端口号，或关闭占用 8000 端口的程序

### 中文乱码
**原因**：系统缺少中文字体
**解决**：
- Windows：自带 SimHei、Microsoft YaHei
- macOS：安装 Arial Unicode MS
- Linux：`sudo apt-get install fonts-wqy-zenhei`

---

## 🚀 扩展建议

- [ ] 添加更多图表类型（热力图、箱线图、雷达图）
- [ ] 支持更多文档格式（PDF、DOCX、Excel）
- [ ] 实现流式输出，实时显示分析进度
- [ ] 添加用户认证和权限管理
- [ ] 支持多数据源（数据库、API）
- [ ] 集成更多 LLM 模型（OpenAI、Claude）
- [ ] 导出 PDF 报告
- [ ] 交互式图表（Plotly、ECharts）

---

## 📄 License

MIT License

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化 Web 框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Matplotlib](https://matplotlib.org/) - 数据可视化
- [Pandas](https://pandas.pydata.org/) - 数据处理
- [DashScope](https://dashscope.aliyun.com/) - 阿里云大模型服务

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**


</div>
