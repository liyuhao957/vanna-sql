import os
from fastapi import FastAPI, Request, UploadFile, File, Form, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import shutil
import json
import datetime
import threading

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

# 记录最近一次生成的SQL
LAST_SQL = {'sql': None}

@app.post("/api/fix_sql_auto")
async def fix_sql_auto(error_message: str = Form(...)):
    """自动修正：只需报错信息，自动获取最近SQL"""
    if not LAST_SQL['sql']:
        return {"success": False, "msg": "未找到最近生成的SQL，请先生成SQL。"}
    prompt = f"""你是SQL修正专家。下面有一个原始SQL和数据库报错信息。\n请严格遵循以下要求：\n1. 只修正导致报错的部分；\n2. 不要重写SQL结构，不要改变查询目标和业务逻辑；\n3. 只输出修正后的SQL，不要解释。\n\n原始SQL：\n{LAST_SQL['sql']}\n\n数据库报错信息：\n{error_message}\n"""
    try:
        response = client.chat.completions.create(
            model="grok-3-beta",
            messages=[{"role": "user", "content": prompt}]
        )
        fixed_sql = response.choices[0].message.content.strip()
        return {"success": True, "fixed_sql": fixed_sql}
    except Exception as e:
        return {"success": False, "msg": f"修正失败: {e}"}

@app.post("/api/fix_sql_manual")
async def fix_sql_manual(sql: str = Form(...), error_message: str = Form(...)):
    """手动修正：用户输入SQL和报错信息"""
    prompt = f"""你是SQL修正专家。下面有一个原始SQL和数据库报错信息。\n请严格遵循以下要求：\n1. 只修正导致报错的部分；\n2. 不要重写SQL结构，不要改变查询目标和业务逻辑；\n3. 只输出修正后的SQL，不要解释。\n\n原始SQL：\n{sql}\n\n数据库报错信息：\n{error_message}\n"""
    try:
        response = client.chat.completions.create(
            model="grok-3-beta",
            messages=[{"role": "user", "content": prompt}]
        )
        fixed_sql = response.choices[0].message.content.strip()
        return {"success": True, "fixed_sql": fixed_sql}
    except Exception as e:
        return {"success": False, "msg": f"修正失败: {e}"}

# 修改SQL生成接口，记录最近一次SQL
@app.post("/api/generate_sql")
async def generate_sql(question: str = Form(...)):
    try:
        sql = vn.generate_sql(question)
        sql_with_prefix = f"%%sql\n{sql.strip()}"
        LAST_SQL['sql'] = sql_with_prefix
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

@app.post("/api/optimize_sql_with_rag")
async def optimize_sql_with_rag(
    user_intent: str = Form(...),
    original_sql: str = Form(...),
    query_result: str = Form("")
):
    """结果不符时的SQL优化，自动拼接RAG上下文"""
    try:
        # 获取RAG上下文（DDL、文档、历史SQL等）
        rag_context = vn.get_context(user_intent)
        prompt = f"""
你是SQL优化专家。下面有数据库结构、字段说明、历史示例、原始SQL、实际查询结果和用户的真实需求描述。
请根据所有信息，优化SQL，使其能正确返回用户想要的结果。
【数据库结构和字段说明】
{rag_context}

【原始SQL】
{original_sql}

【实际查询结果】
{query_result or '（无）'}

【用户真实需求描述】
{user_intent}
只输出优化后的SQL，不要解释。
"""
        response = client.chat.completions.create(
            model="grok-3-beta",
            messages=[{"role": "user", "content": prompt}]
        )
        optimized_sql = response.choices[0].message.content.strip()
        return {"success": True, "optimized_sql": optimized_sql}
    except Exception as e:
        return {"success": False, "msg": f"SQL优化失败: {e}"}

RULES_FILE = "rules.json"
RULES_LOCK = threading.Lock()

def load_rules():
    if not os.path.exists(RULES_FILE):
        # 初始化最佳实践规则
        default_rules = [
            {"type": "宽表分区过滤", "tables": ["large_table", "fact_table"], "partition_field": "timed"},
            {"type": "大表ORDER BY限制", "tables": ["large_table"], "forbid_order_by": True},
            {"type": "禁止全表扫描", "tables": ["large_table", "fact_table"]},
            {"type": "JOIN分区字段", "tables": ["large_table"], "partition_field": "timed"},
            {"type": "窗口函数推荐", "other": "ROW_NUMBER() OVER(), DENSE_RANK() OVER(), LEAD(), LAG()"},
            {"type": "CTE推荐", "other": "WITH temp_table AS (SELECT ... FROM ...)"},
            {"type": "复杂查询优化", "other": "物化视图、合适JOIN、索引、CBO优化、执行计划优化"},
            {"type": "JOIN顺序优化", "other": "大表做左表，小表做Hash表"},
            {"type": "行转列推荐", "other": "Lateral Join"},
            {"type": "分页优化", "other": "OFFSET分页"}
        ]
        save_rules(default_rules)
        return default_rules
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        try:
            rules = json.load(f)
            if not rules:
                # 文件存在但为空，也写入默认规则
                default_rules = [
                    {"type": "宽表分区过滤", "tables": ["large_table", "fact_table"], "partition_field": "timed"},
                    {"type": "大表ORDER BY限制", "tables": ["large_table"], "forbid_order_by": True},
                    {"type": "禁止全表扫描", "tables": ["large_table", "fact_table"]},
                    {"type": "JOIN分区字段", "tables": ["large_table"], "partition_field": "timed"},
                    {"type": "窗口函数推荐", "other": "ROW_NUMBER() OVER(), DENSE_RANK() OVER(), LEAD(), LAG()"},
                    {"type": "CTE推荐", "other": "WITH temp_table AS (SELECT ... FROM ...)"},
                    {"type": "复杂查询优化", "other": "物化视图、合适JOIN、索引、CBO优化、执行计划优化"},
                    {"type": "JOIN顺序优化", "other": "大表做左表，小表做Hash表"},
                    {"type": "行转列推荐", "other": "Lateral Join"},
                    {"type": "分页优化", "other": "OFFSET分页"}
                ]
                save_rules(default_rules)
                return default_rules
            return rules
        except Exception:
            # 文件损坏等异常也写入默认规则
            default_rules = [
                {"type": "宽表分区过滤", "tables": ["large_table", "fact_table"], "partition_field": "timed"},
                {"type": "大表ORDER BY限制", "tables": ["large_table"], "forbid_order_by": True},
                {"type": "禁止全表扫描", "tables": ["large_table", "fact_table"]},
                {"type": "JOIN分区字段", "tables": ["large_table"], "partition_field": "timed"},
                {"type": "窗口函数推荐", "other": "ROW_NUMBER() OVER(), DENSE_RANK() OVER(), LEAD(), LAG()"},
                {"type": "CTE推荐", "other": "WITH temp_table AS (SELECT ... FROM ...)"},
                {"type": "复杂查询优化", "other": "物化视图、合适JOIN、索引、CBO优化、执行计划优化"},
                {"type": "JOIN顺序优化", "other": "大表做左表，小表做Hash表"},
                {"type": "行转列推荐", "other": "Lateral Join"},
                {"type": "分页优化", "other": "OFFSET分页"}
            ]
            save_rules(default_rules)
            return default_rules

def save_rules(rules):
    with RULES_LOCK:
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)

@app.get("/api/rules")
def get_rules():
    return load_rules()

@app.post("/api/rules")
async def add_rule(
    rule_type: str = Form(...),
    tables: str = Form(""),
    partition_field: str = Form(""),
    forbid_order_by: str = Form(""),
    other: str = Form("")
):
    rules = load_rules()
    rule = {"type": rule_type}
    if tables:
        rule["tables"] = [t.strip() for t in tables.split(",") if t.strip()]
    if partition_field:
        rule["partition_field"] = partition_field.strip()
    if forbid_order_by:
        rule["forbid_order_by"] = forbid_order_by.lower() == "true"
    if other:
        rule["other"] = other
    rules.append(rule)
    save_rules(rules)
    return {"success": True}

@app.put("/api/rules")
async def edit_rule(
    idx: int = Form(...),
    rule_type: str = Form(...),
    tables: str = Form(""),
    partition_field: str = Form(""),
    forbid_order_by: str = Form(""),
    other: str = Form("")
):
    rules = load_rules()
    if idx < 0 or idx >= len(rules):
        return {"success": False, "msg": "规则索引无效"}
    rule = {"type": rule_type}
    if tables:
        rule["tables"] = [t.strip() for t in tables.split(",") if t.strip()]
    if partition_field:
        rule["partition_field"] = partition_field.strip()
    if forbid_order_by:
        rule["forbid_order_by"] = forbid_order_by.lower() == "true"
    if other:
        rule["other"] = other
    rules[idx] = rule
    save_rules(rules)
    return {"success": True}

@app.delete("/api/rules")
async def delete_rule(idx: int = Form(...)):
    rules = load_rules()
    if idx < 0 or idx >= len(rules):
        return {"success": False, "msg": "规则索引无效"}
    rules.pop(idx)
    save_rules(rules)
    return {"success": True}

# ------------------ 启动入口 ------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5173, reload=True) 