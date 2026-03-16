from agents.task_planning_agent import TaskPlanningAgent
from agents.data_analysis_agent import DataAnalysisAgent
from agents.report_generation_agent import ReportGenerationAgent
from agents.quality_control_agent import QualityControlAgent
from storage.redis_memory import RedisMemory
from storage.chroma_store import ChromaVectorStore
from mcp.mcp_client import MCPClient
from knowledge.knowledge_base import KnowledgeBase
import uuid
import json
import asyncio
from typing import Optional


class MultiAgentOrchestrator:
    def __init__(self):
        self.task_planner = TaskPlanningAgent()
        self.data_analyst = DataAnalysisAgent()
        self.report_generator = ReportGenerationAgent()
        self.quality_controller = QualityControlAgent()
        self.redis_memory = RedisMemory()
        self.vector_store = ChromaVectorStore()

        # 初始化MCP客户端
        self.mcp_client = MCPClient()

        # 为所有agent设置MCP客户端
        self.task_planner.set_mcp_client(self.mcp_client)
        self.data_analyst.set_mcp_client(self.mcp_client)
        self.report_generator.set_mcp_client(self.mcp_client)
        self.quality_controller.set_mcp_client(self.mcp_client)

        # 为数据分析agent设置向量库（用于存储Amazon搜索结果）
        self.data_analyst.set_vector_store(self.vector_store)

        # 初始化知识库
        self.knowledge_base = KnowledgeBase()


    async def process_request_async(self, user_request: str, data_path: Optional[str] = None):
        """异步处理请求，支持MCP工具调用"""
        session_id = str(uuid.uuid4())
        print(f"[会话ID] {session_id}")

        # 1. 从知识库检索相关信息
        print("\n[步骤0] 检索知识库...")
        kb_results = self.knowledge_base.search(user_request, n_results=3)
        kb_context = "\n".join([r["content"] for r in kb_results])
        print(f"找到 {len(kb_results)} 条相关知识")

        # 2. 任务规划（异步）
        print("\n[步骤1] 任务规划中...")
        task_plan_prompt = f"用户请求: {user_request}\n\n相关知识:\n{kb_context}\n\n请生成JSON格式的任务执行计划。"

        try:
            print("[步骤1] 等待LLM响应...")
            task_plan_response = await asyncio.wait_for(
                self.task_planner.execute_async(task_plan_prompt),
                timeout=30.0  # 30秒超时
            )

            print(f"[步骤1] 收到响应，长度: {len(task_plan_response)} 字符")
            print(f"[步骤1] 响应预览: {task_plan_response[:200]}...")

            # 尝试解析JSON
            try:
                print("[步骤1] 尝试解析JSON...")
                task_plan = json.loads(task_plan_response)
                print("[步骤1] JSON解析成功")
            except Exception as json_error:
                # 如果不是JSON，包装成简单格式
                print(f"[步骤1] JSON解析失败: {json_error}，使用默认格式")
                task_plan = {"plan": task_plan_response, "tasks": []}

        except asyncio.TimeoutError:
            print("[警告] 任务规划超时，使用默认计划")
            task_plan = {"plan": "默认任务计划", "tasks": []}
        except Exception as e:
            print(f"[错误] 任务规划失败: {e}")
            import traceback
            traceback.print_exc()
            task_plan = {"plan": f"错误: {str(e)}", "tasks": []}

        print("[步骤1] 准备存储到Redis...")
        self.redis_memory.store(f"plan:{session_id}", task_plan)
        print("[步骤1] 存储完成")
        print(f"任务计划: {json.dumps(task_plan, ensure_ascii=False, indent=2)}")

        # 3. 数据分析（异步）
        print("\n[步骤2] 数据分析中...")
        try:
            if data_path:
                analysis_result = await asyncio.wait_for(
                    self.data_analyst.analyze_data_async(data_path, user_request),
                    timeout=60.0  # 60秒超时
                )
            else:
                analysis_prompt = f"用户请求: {user_request}\n知识库上下文: {kb_context}"
                analysis_response = await asyncio.wait_for(
                    self.data_analyst.execute_async(analysis_prompt),
                    timeout=60.0
                )
                try:
                    analysis_result = json.loads(analysis_response)
                except:
                    analysis_result = {"analysis": analysis_response}

        except asyncio.TimeoutError:
            print("[警告] 数据分析超时")
            analysis_result = {"error": "分析超时", "summary": "数据分析超时"}
        except Exception as e:
            print(f"[错误] 数据分析失败: {e}")
            analysis_result = {"error": str(e), "summary": f"分析失败: {str(e)}"}

        self.redis_memory.store(f"analysis:{session_id}", analysis_result)
        print(f"分析结果: {json.dumps(analysis_result, ensure_ascii=False, indent=2)}")

        # 4. 生成报告（异步，带图表）
        print("\n[步骤3] 生成报告中...")
        try:
            report_result = await asyncio.wait_for(
                self.report_generator.generate_report_with_charts(
                    analysis_result,
                    data_path=data_path
                ),
                timeout=120.0  # 60秒超时
            )
            report = report_result.get("report", "")
            chart_paths = report_result.get("chart_paths", [])

        except asyncio.TimeoutError:
            print("[警告] 报告生成超时")
            report = "报告生成超时"
            chart_paths = []
        except Exception as e:
            print(f"[错误] 报告生成失败: {e}")
            report = f"报告生成失败: {str(e)}"
            chart_paths = []

        self.redis_memory.store(f"report:{session_id}", report)
        print(f"\n报告:\n{report}")

        if chart_paths:
            print(f"\n[图表] 已生成 {len(chart_paths)} 个图表:")
            for path in chart_paths:
                print(f"  - {path}")

        # 5. 质量控制（异步）- 支持重试机制
        max_retries = 2  # 最多重试2次
        retry_count = 0

        while retry_count <= max_retries:
            print(f"\n[步骤4] 质量检查中... (尝试 {retry_count + 1}/{max_retries + 1})")
            try:
                quality_prompt = f"分析结果: {json.dumps(analysis_result, ensure_ascii=False)}\n报告: {report}"
                quality_response = await asyncio.wait_for(
                    self.quality_controller.execute_async(quality_prompt),
                    timeout=240.0  # 增加到240秒超时（deepseek-r1需要更长时间）
                )

                try:
                    # 尝试提取 JSON（可能被包裹在 markdown 代码块中）
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', quality_response, re.DOTALL)
                    if json_match:
                        quality_check = json.loads(json_match.group(1))
                    else:
                        quality_check = json.loads(quality_response)

                    # 如果有嵌套的 approved 字段，使用内层的
                    if "note" in quality_check and isinstance(quality_check.get("note"), str):
                        try:
                            inner_json = json.loads(quality_check["note"])
                            if "approved" in inner_json:
                                quality_check = inner_json
                        except:
                            pass

                except:
                    quality_check = {"approved": True, "note": quality_response}

            except asyncio.TimeoutError:
                print("[警告] 质量检查超时（deepseek-r1响应较慢），默认通过")
                quality_check = {"approved": True, "note": "质量检查超时"}
            except Exception as e:
                print(f"[错误] 质量检查失败: {e}")
                quality_check = {"approved": True, "error": str(e)}

            print(f"质量评估: {json.dumps(quality_check, ensure_ascii=False, indent=2)}")

            # 如果质量不过关且还有重试次数，重新分析
            if not quality_check.get("approved", False) and retry_count < max_retries:
                print(f"\n[质量不合格] 准备重新分析... (第 {retry_count + 1} 次重试)")
                print(f"问题: {quality_check.get('issues', [])}")
                print(f"建议: {quality_check.get('corrections', [])}")

                retry_count += 1

                # 重新进行数据分析，加入质量反馈
                print(f"\n[步骤2-重试{retry_count}] 重新数据分析中...")
                feedback = f"\n\n质量反馈:\n问题: {quality_check.get('issues', [])}\n改进建议: {quality_check.get('corrections', [])}"

                try:
                    if data_path:
                        analysis_result = await asyncio.wait_for(
                            self.data_analyst.analyze_data_async(data_path, user_request + feedback),
                            timeout=60.0
                        )
                    else:
                        analysis_prompt = f"用户请求: {user_request}\n知识库上下文: {kb_context}{feedback}"
                        analysis_response = await asyncio.wait_for(
                            self.data_analyst.execute_async(analysis_prompt),
                            timeout=60.0
                        )
                        try:
                            analysis_result = json.loads(analysis_response)
                        except:
                            analysis_result = {"analysis": analysis_response}
                except Exception as e:
                    print(f"[错误] 重新分析失败: {e}")
                    break

                # 重新生成报告
                print(f"\n[步骤3-重试{retry_count}] 重新生成报告中...")
                try:
                    report_result = await asyncio.wait_for(
                        self.report_generator.generate_report_with_charts(
                            analysis_result,
                            data_path=data_path
                        ),
                        timeout=60.0
                    )
                    report = report_result.get("report", "")
                    chart_paths = report_result.get("chart_paths", [])
                except Exception as e:
                    print(f"[错误] 重新生成报告失败: {e}")
                    break

                print(f"\n重新生成的报告:\n{report}")
                # 继续下一轮质量检查
            else:
                # 质量合格或已达到最大重试次数，退出循环
                break

        # 6. 存储到向量库
        if quality_check.get("approved", False):
            try:
                # 确保元数据只包含简单类型
                metadata = {
                    "request": str(user_request),
                    "score": float(quality_check.get("credibility_score", 0.0)) if quality_check.get("credibility_score") else 0.0,
                    "session_id": str(session_id)
                }
                self.vector_store.add_analysis_result(
                    session_id,
                    report,
                    metadata
                )
                print("\n[完成] 分析结果已存储到知识库")
            except Exception as e:
                print(f"\n[警告] 存储到向量库失败: {e}")
                # 不影响主流程，继续执行
        else:
            print(f"\n[警告] 经过 {retry_count} 次重试后，质量仍不合格，未存储到知识库")

        return {
            "session_id": session_id,
            "task_plan": task_plan,
            "analysis": analysis_result,
            "report": report,
            "quality": quality_check,
            "kb_context": kb_results,
            "chart_paths": chart_paths,
            "retry_count": retry_count
        }

    def rebuild_knowledge_base(self):
        """重建知识库"""
        print("\n[知识库] 开始重建...")
        stats = self.knowledge_base.rebuild_index()
        print(f"[知识库] 重建完成: {stats}")
        return stats
