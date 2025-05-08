import os
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import shutil
import json
import datetime

# 本地私有化Vanna初始化
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# 请替换为你自己的openai或xai key
from openai import OpenAI
client = OpenAI(
    api_key="xai-WvUhgZsGciGI1CKwiVnBnBVPzbNMRzXBPjr4rPa9Eq6Y524LowNPBikgmRfJKkNJefZY60f4fdzw5PJ7",
    base_url="https://api.x.ai/v1"
)

# 初始化Vanna
vn = MyVanna(config={
    'model': 'grok-3-beta',
    'n_results': 20,  # 检索数量改为20条
    # 'path': 'your_chromadb_path',  # 可选，指定本地向量库路径
})
vn.client = client  # 用新版OpenAI类实例

# ------------------ FastAPI初始化 ------------------
app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（前端页面）
if not os.path.exists("frontend"):
    os.makedirs("frontend")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ------------------ API接口 ------------------

@app.get("/")
def index():
    """首页，重定向到前端页面"""
    return FileResponse("frontend/index.html")

@app.post("/api/train")
async def train(
    ddl: Optional[str] = Form(None),
    documentation: Optional[str] = Form(None),
    sql: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    question_sql: Optional[str] = Form(None)
):
    """训练接口，支持多种训练方式"""
    try:
        if ddl:
            vn.train(ddl=ddl)
        if documentation:
            vn.train(documentation=documentation)
        if sql:
            vn.train(sql=sql)
        if question and question_sql:
            vn.train(question=question, sql=question_sql)
        return {"success": True, "msg": "训练成功"}
    except Exception as e:
        return {"success": False, "msg": f"训练失败: {e}"}

@app.post("/api/generate_sql")
async def generate_sql(question: str = Form(...)):
    """生成SQL接口"""
    try:
        sql = vn.generate_sql(question)
        sql_with_prefix = f"%%sql\n{sql.strip()}"
        return {"success": True, "sql": sql_with_prefix}
    except Exception as e:
        return {"success": False, "msg": f"生成SQL失败: {e}"}

@app.get("/api/training_data")
def get_training_data():
    """查看所有训练数据"""
    try:
        df = vn.get_training_data()
        print(df.head())  # 新增：调试输出DataFrame内容
        data = df.to_dict(orient="records")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "msg": f"获取训练数据失败: {e}"}

@app.post("/api/delete_training_data")
async def delete_training_data(id: str = Form(...)):
    """删除指定训练数据"""
    try:
        vn.remove_training_data(id=id)
        return {"success": True, "msg": "删除成功"}
    except Exception as e:
        return {"success": False, "msg": f"删除失败: {e}"}

FEEDBACK_LOG = "feedback_log.json"

def save_feedback_log(question, sql, feedback_type):
    log = []
    if os.path.exists(FEEDBACK_LOG):
        with open(FEEDBACK_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
    log.append({
        "question": question,
        "sql": sql,
        "type": feedback_type,
        "time": datetime.datetime.now().isoformat()
    })
    with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

@app.post("/api/feedback")
async def feedback(question: str = Form(...), sql: str = Form(...), feedback_type: str = Form("correct")):
    try:
        vn.train(question=question, sql=sql)
        save_feedback_log(question, sql, feedback_type)
        return {"success": True, "msg": "反馈已保存，系统已学习"}
    except Exception as e:
        return {"success": False, "msg": f"反馈保存失败: {e}"}

@app.get("/api/feedback_history")
def feedback_history():
    try:
        if os.path.exists(FEEDBACK_LOG):
            with open(FEEDBACK_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"success": True, "data": data}
        else:
            return {"success": True, "data": []}
    except Exception as e:
        return {"success": False, "msg": f"获取反馈历史失败: {e}"}

@app.post("/api/delete_feedback")
async def delete_feedback(time: str = Form(...)):
    try:
        # 只从feedback_log.json中删除，不影响主训练库
        if not os.path.exists(FEEDBACK_LOG):
            return {"success": False, "msg": "反馈日志不存在"}
        with open(FEEDBACK_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
        new_log = [item for item in log if item.get("time") != time]
        with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
            json.dump(new_log, f, ensure_ascii=False, indent=2)
        return {"success": True, "msg": "反馈已撤销（仅日志）"}
    except Exception as e:
        return {"success": False, "msg": f"撤销失败: {e}"}

# ------------------ 启动入口 ------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5173, reload=True) 