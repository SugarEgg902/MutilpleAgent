class Config:
    # 通义千问配置
    DASHSCOPE_API_KEY = "sk-4555565c053f4e958697a48303b74534"

    # 模型配置
    MODEL = "qwen3-max"  # 默认模型（用于一般任务）
    ORCHESTRA_MODEL = "deepseek-r1"  # 编排模型（用于质量控制等高级任务）

    # 可选：为不同Agent指定不同模型
    TASK_PLANNING_MODEL = "qwen3-max"  # 任务规划
    DATA_ANALYSIS_MODEL = "qwen3-max"  # 数据分析
    REPORT_GENERATION_MODEL = "qwen3-max"  # 报告生成
    QUALITY_CONTROL_MODEL = "deepseek-r1"  # 质量控制（使用更强模型）

    # Redis配置
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379

    # Chroma配置
    CHROMA_PERSIST_DIR = "./chroma_db"

    # 知识库配置
    KNOWLEDGE_BASE_DIR = "./knowledgeBase"
    MD5_DIR = "./MD5"
    CHROMA_KB_DIR = "./chroma_kb"
