from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio
import json
from datetime import datetime
from core.orchestrator import MultiAgentOrchestrator

app = FastAPI(title="多智能体数据分析系统")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化orchestrator
orchestrator = MultiAgentOrchestrator()

# 存储历史记录
history = []

# 确保目录存在
os.makedirs("data", exist_ok=True)
os.makedirs("knowledgeBase", exist_ok=True)
os.makedirs("charts", exist_ok=True)
os.makedirs("static", exist_ok=True)


class QueryRequest(BaseModel):
    question: str
    data_file: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回前端页面"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload/knowledge")
async def upload_knowledge(file: UploadFile = File(...)):
    """上传知识库文件"""
    try:
        file_path = os.path.join("knowledge", "knowledgeBase", file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 重建知识库索引
        stats = orchestrator.rebuild_knowledge_base()

        return {
            "success": True,
            "message": f"知识库文件 {file.filename} 上传成功",
            "file_path": file_path,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/data")
async def upload_data(file: UploadFile = File(...)):
    """上传销售数据文件"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持CSV文件")

        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return {
            "success": True,
            "message": f"数据文件 {file.filename} 上传成功",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(request: QueryRequest):
    """处理用户查询"""
    try:
        print(f"\n[Web API] 收到查询: {request.question}")

        # 构建数据文件路径（使用正斜杠避免转义问题）
        data_path = None
        if request.data_file:
            data_path = os.path.abspath(os.path.join("data", request.data_file))
            # 转换为正斜杠路径，避免反斜杠转义问题
            data_path = data_path.replace('\\', '/')
            if not os.path.exists(data_path):
                raise HTTPException(status_code=404, detail=f"数据文件不存在: {request.data_file}")
            print(f"[Web API] 使用指定数据文件: {data_path}")
        else:
            # 如果没有指定文件，自动读取 data 文件夹下所有 CSV 文件
            csv_files = [f for f in os.listdir("data") if f.endswith('.csv')]
            if csv_files:
                # 如果有多个文件，使用第一个
                data_path = os.path.abspath(os.path.join("data", csv_files[0]))
                # 转换为正斜杠路径
                print(f"原始文件路径：{data_path}")
                data_path = data_path.replace('\\', '/')
                print(f"[Web API] 未指定数据文件，自动使用: {data_path}")
            else:
                print("[Web API] data 文件夹下没有 CSV 文件")

        # 异步处理请求
        result = await orchestrator.process_request_async(
            user_request=request.question,
            data_path=data_path
        )

        # 添加到历史记录
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "question": request.question,
            "data_file": request.data_file,
            "result": result
        }
        history.append(history_item)

        # 只保留最近50条记录
        if len(history) > 50:
            history.pop(0)

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history():
    """获取历史记录"""
    return {
        "success": True,
        "history": history
    }


@app.get("/files/data")
async def list_data_files():
    """列出所有数据文件"""
    try:
        files = [f for f in os.listdir("data") if f.endswith('.csv')]
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/knowledge")
async def list_knowledge_files():
    """列出所有知识库文件"""
    try:
        files = os.listdir("Knowledge/KnowledgeBase")
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/charts/{filename}")
async def get_chart(filename: str):
    """获取图表文件"""
    file_path = os.path.join("charts", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图表文件不存在")

    from fastapi.responses import FileResponse
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
