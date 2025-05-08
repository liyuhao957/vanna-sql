#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
import io
import sys
import platform
import os
import traceback
import shutil
import json
from typing import Union, Dict, List, Any

# 设置正确的本地化和编码
locale.setlocale(locale.LC_ALL, '')  # 使用系统默认locale
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
os.environ['LC_CTYPE'] = 'UTF-8'

# 检测是否是macOS系统
IS_MACOS = platform.system() == 'Darwin'

# 打印函数，处理中文字符显示问题
def print_fixed(text):
    """修复中文字符在终端中的显示问题"""
    if IS_MACOS:
        # 在macOS上，使用特殊方法处理中文显示
        # 这里使用一个技巧：将字符串中的中文字符单独输出，不使用print的空格拼接
        for char in str(text):
            sys.stdout.write(char)
        sys.stdout.write('\n')
        sys.stdout.flush()
    else:
        # 在其他系统上使用正常的print
        print(text)

from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat
import pandas as pd
from openai import OpenAI

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# 创建OpenAI客户端
client = OpenAI(
    api_key="xai-WvUhgZsGciGI1CKwiVnBnBVPzbNMRzXBPjr4rPa9Eq6Y524LowNPBikgmRfJKkNJefZY60f4fdzw5PJ7",
    base_url="https://api.x.ai/v1"
)

# 初始化Vanna(使用OpenAI客户端)
vn = MyVanna(config={
    'model': 'grok-3-beta'
})

# 通过构造函数设置client
vn.client = client

# 创建数据目录
os.makedirs('data', exist_ok=True)

# 新增：数据分析函数
def analyze_data_with_ai(original_question: str, sql: str, data: Union[pd.DataFrame, str, Dict, List], analysis_question: str) -> str:
    """
    使用OpenAI分析数据结果
    
    参数:
        original_question (str): 原始用户问题
        sql (str): 执行的SQL查询
        data (Union[pd.DataFrame, str, Dict, List]): 数据结果，可以是pandas DataFrame、字符串或JSON兼容的对象
        analysis_question (str): 针对数据的具体分析问题
        
    返回:
        str: AI生成的分析结果
    """
    # 将数据转换为字符串表示
    if isinstance(data, pd.DataFrame):
        if len(data) > 50:
            # 如果数据过大，只使用前50行
            data_str = data.head(50).to_string(index=False) + "\n... [数据已截断，仅显示前50行]"
        else:
            data_str = data.to_string(index=False)
    elif isinstance(data, (dict, list)):
        # 将JSON对象转换为格式化字符串
        try:
            data_str = json.dumps(data, indent=2, ensure_ascii=False)
            if len(data_str) > 5000:  # 约5000个字符的限制
                data_str = data_str[:5000] + "... [数据已截断]"
        except Exception as e:
            data_str = f"无法处理JSON数据: {str(e)}"
    else:
        # 假设它已经是字符串
        data_str = str(data)
        if len(data_str) > 5000:  # 字符限制
            data_str = data_str[:5000] + "... [数据已截断]"
    
    # 构建prompt
    prompt = f"""
    原始问题: {original_question}
    执行的SQL: {sql}
    
    数据结果:
    {data_str}
    
    分析问题: {analysis_question}
    
    请分析上述数据，回答用户的分析问题。提供具体见解，包括数据趋势、异常值及可能的原因。
    如果数据中有明显的模式或异常，请指出并解释可能的业务原因。
    如果分析需要额外信息，请说明需要哪些补充数据能够提供更全面的分析。
    """
    
    # 记录分析请求
    with open('data/analysis_requests.txt', 'a', encoding='utf-8') as f:
        f.write(f"时间: {pd.Timestamp.now()}\n")
        f.write(f"原始问题: {original_question}\n")
        f.write(f"分析问题: {analysis_question}\n")
        f.write(f"SQL: {sql}\n")
        f.write(f"数据大小: {len(data) if isinstance(data, pd.DataFrame) else '未知'} 行\n")
        f.write("-" * 50 + "\n\n")
    
    # 调用OpenAI API
    try:
        response = client.chat.completions.create(
            model="grok-3-beta",  # 使用配置的模型
            messages=[{"role": "user", "content": prompt}]
        )
        analysis_result = response.choices[0].message.content
        
        # 记录分析结果
        with open('data/analysis_results.txt', 'a', encoding='utf-8') as f:
            f.write(f"时间: {pd.Timestamp.now()}\n")
            f.write(f"分析问题: {analysis_question}\n")
            f.write(f"分析结果:\n{analysis_result}\n")
            f.write("-" * 50 + "\n\n")
        
        return analysis_result
    except Exception as e:
        error_msg = f"分析过程中出错: {str(e)}"
        print_fixed(error_msg)
        traceback.print_exc()
        return error_msg

# 训练函数
def train_with_ddl(ddl_text=None, ddl_file=None):
    """使用DDL进行训练"""
    if ddl_file:
        with open(ddl_file, 'r') as f:
            ddl_text = f.read()
    
    if not ddl_text:
        print_fixed("错误: 未提供DDL文本或文件")
        return
        
    vn.train(ddl=ddl_text)
    print_fixed("DDL训练完成")
    
    # 保存到文件以备记录
    with open('data/trained_ddl.sql', 'a') as f:
        f.write(ddl_text + "\n\n")

def train_with_sql(sql_text=None, sql_file=None):
    """使用SQL示例进行训练"""
    if sql_file:
        with open(sql_file, 'r') as f:
            sql_text = f.read()
    
    if not sql_text:
        print_fixed("错误: 未提供SQL文本或文件")
        return
        
    vn.train(sql=sql_text)
    print_fixed("SQL训练完成")
    
    # 保存到文件以备记录
    with open('data/trained_sql.sql', 'a') as f:
        f.write(sql_text + "\n\n")

def train_with_doc(doc_text=None, doc_file=None):
    """使用文档进行训练"""
    if doc_file:
        with open(doc_file, 'r') as f:
            doc_text = f.read()
    
    if not doc_text:
        print_fixed("错误: 未提供文档文本或文件")
        return
        
    vn.train(documentation=doc_text)
    print_fixed("文档训练完成")
    
    # 保存到文件以备记录
    with open('data/trained_docs.txt', 'a') as f:
        f.write(doc_text + "\n\n")

def train_with_question_sql(question=None, sql=None, file=None):
    """使用问题-SQL对进行训练，这是最直接且最有效的训练方式"""
    if file:
        # 从文件中读取问题-SQL对
        pairs = []
        current_question = None
        current_sql = ""
        
        with open(file, 'r') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("问题:") or line.startswith("question:"):
                    # 如果已经有一个问题-SQL对，先保存它
                    if current_question and current_sql:
                        pairs.append((current_question, current_sql))
                    
                    # 开始新的问题
                    current_question = line.split(":", 1)[1].strip()
                    current_sql = ""
                elif line.startswith("SQL:") or line.startswith("sql:"):
                    # 开始收集SQL
                    j = i + 1
                    sql_content = []
                    
                    # 继续读取SQL直到下一个问题或文件结束
                    while j < len(lines) and not (lines[j].strip().startswith("问题:") or 
                                                  lines[j].strip().startswith("question:")):
                        sql_content.append(lines[j])
                        j += 1
                    
                    current_sql = "".join(sql_content).strip()
                    i = j - 1  # 更新i，下一轮循环会+1
                
                i += 1
            
            # 添加最后一个问题-SQL对
            if current_question and current_sql:
                pairs.append((current_question, current_sql))
        
        # 训练每一个问题-SQL对
        if not pairs:
            print_fixed("错误: 未在文件中找到有效的问题-SQL对")
            return
        
        for q, s in pairs:
            vn.train(question=q, sql=s)
            print_fixed(f"训练问题: {q}")
            
            # 保存到文件以备记录
            with open('data/trained_question_sql.txt', 'a') as f:
                f.write(f"问题: {q}\nSQL: {s}\n\n")
        
        print_fixed(f"成功训练了 {len(pairs)} 个问题-SQL对")
    
    elif question and sql:
        # 直接使用提供的问题和SQL进行训练
        vn.train(question=question, sql=sql)
        print_fixed(f"训练问题: {question}")
        
        # 保存到文件以备记录
        with open('data/trained_question_sql.txt', 'a') as f:
            f.write(f"问题: {question}\nSQL: {sql}\n\n")
    else:
        print_fixed("错误: 需要提供问题和SQL，或者包含问题-SQL对的文件")

# 问答函数
def ask_question(question):
    """根据问题生成SQL"""
    sql = vn.generate_sql(question)
    print_fixed("\n问题:")
    print_fixed(question)
    print_fixed("\n生成的SQL:")
    print_fixed(sql)
    print_fixed("\n将此SQL复制到Jupyter中执行以获取结果\n")
    
    # 保存到文件以备记录
    with open('data/generated_queries.sql', 'a') as f:
        f.write(f"-- 问题: {question}\n{sql}\n\n")
    
    return sql

# 完整的问答功能，类似于vn.ask
def ask_full(question):
    """完整的问答功能，包括生成SQL、执行SQL和生成图表"""
    print_fixed("生成SQL中...")
    sql = vn.generate_sql(question)
    print_fixed("SQL生成完成:")
    print_fixed(sql)
    
    print_fixed("\n执行SQL中...")
    try:
        # 注意：这需要配置数据库连接
        # results = vn.run_sql(sql)
        # print("SQL执行结果:")
        # print(results.head())
        
        # print("\n生成可视化图表...")
        # 注意：这需要Plotly支持
        # should_plot = vn.should_generate_chart(question, sql, results)
        # if should_plot:
        #     fig = vn.get_plotly_figure(question, sql, results)
        #     fig.show()
        # else:
        #     print("此查询结果不适合生成图表")
        
        print_fixed("由于未配置数据库连接，无法执行SQL和生成图表")
    except Exception as e:
        print_fixed(f"执行出错: {str(e)}")
    
    return sql

# 保存和加载训练数据
def save_database(filename="vanna_db"):
    """保存向量数据库"""
    try:
        # 创建保存目录
        save_dir = os.path.join('data', filename)
        os.makedirs(save_dir, exist_ok=True)
        
        # 将已训练的数据保存到文件
        print_fixed(f"正在保存训练数据到: {save_dir}")
        
        # 将训练记录保存到一个汇总文件
        summary_file = os.path.join(save_dir, "training_summary.txt")
        with open(summary_file, "w") as f:
            f.write("训练数据汇总\n")
            f.write("===========\n\n")
            
            # 添加DDL训练数据
            if os.path.exists('data/trained_ddl.sql'):
                with open('data/trained_ddl.sql', 'r') as ddl_file:
                    ddl_content = ddl_file.read()
                    f.write("## DDL 训练数据\n\n")
                    f.write(ddl_content)
                    f.write("\n\n")
            
            # 添加SQL训练数据
            if os.path.exists('data/trained_sql.sql'):
                with open('data/trained_sql.sql', 'r') as sql_file:
                    sql_content = sql_file.read()
                    f.write("## SQL 训练数据\n\n")
                    f.write(sql_content)
                    f.write("\n\n")
            
            # 添加文档训练数据
            if os.path.exists('data/trained_docs.txt'):
                with open('data/trained_docs.txt', 'r') as doc_file:
                    doc_content = doc_file.read()
                    f.write("## 文档训练数据\n\n")
                    f.write(doc_content)
                    f.write("\n\n")
            
            # 添加问题-SQL对训练数据
            if os.path.exists('data/trained_question_sql.txt'):
                with open('data/trained_question_sql.txt', 'r') as q_sql_file:
                    q_sql_content = q_sql_file.read()
                    f.write("## 问题-SQL对训练数据\n\n")
                    f.write(q_sql_content)
                    f.write("\n\n")
        
        # 复制各个训练文件
        for file_name in ['trained_ddl.sql', 'trained_sql.sql', 'trained_docs.txt', 'trained_question_sql.txt', 'generated_queries.sql']:
            src_path = os.path.join('data', file_name)
            if os.path.exists(src_path):
                dst_path = os.path.join(save_dir, file_name)
                shutil.copy2(src_path, dst_path)
        
        print_fixed(f"训练数据已保存为: {filename}")
        print_fixed(f"注意: 由于Vanna库不支持直接保存向量数据库，只保存了训练输入数据。")
        print_fixed(f"要恢复训练状态，请重新运行训练命令。")
        return True
    except Exception as e:
        print_fixed(f"保存失败: {str(e)}")
        return False

def load_model(filename="vanna_model"):
    """加载训练模型
    
    从指定的模型目录加载训练数据并重新训练模型。
    模型目录通常是通过save_database函数创建的。
    
    参数:
        filename (str): 模型目录名称，默认是"vanna_model"
    
    返回:
        bool: 加载成功返回True，否则返回False
    """
    try:
        # 检查模型目录是否存在
        model_dir = os.path.join('data', filename)
        if not os.path.exists(model_dir):
            print_fixed(f"错误: 模型目录 '{model_dir}' 不存在")
            return False
        
        print_fixed(f"正在从 {model_dir} 加载模型...")
        
        # 创建训练数据目录
        os.makedirs('data', exist_ok=True)
        
        # 加载并应用每种类型的训练数据
        training_files = {
            'trained_ddl.sql': train_with_ddl,
            'trained_sql.sql': train_with_sql,
            'trained_docs.txt': train_with_doc,
            'trained_question_sql.txt': train_with_question_sql
        }
        
        # 复制文件并重新训练
        for file_name, train_func in training_files.items():
            src_path = os.path.join(model_dir, file_name)
            dst_path = os.path.join('data', file_name)
            
            if os.path.exists(src_path):
                # 复制文件到工作目录
                shutil.copy2(src_path, dst_path)
                print_fixed(f"已复制 {file_name}")
                
                # 使用适当的训练函数重新训练
                if file_name == 'trained_ddl.sql':
                    train_func(ddl_file=dst_path)
                elif file_name == 'trained_sql.sql':
                    train_func(sql_file=dst_path)
                elif file_name == 'trained_docs.txt':
                    train_func(doc_file=dst_path)
                elif file_name == 'trained_question_sql.txt':
                    train_func(file=dst_path)
                
                print_fixed(f"已应用 {file_name} 的训练数据")
            else:
                print_fixed(f"警告: 未找到 {file_name} 文件")
        
        # 复制其他相关文件
        other_files = ['generated_queries.sql']
        for file_name in other_files:
            src_path = os.path.join(model_dir, file_name)
            if os.path.exists(src_path):
                dst_path = os.path.join('data', file_name)
                shutil.copy2(src_path, dst_path)
                print_fixed(f"已复制 {file_name}")
        
        print_fixed(f"模型 '{filename}' 加载完成")
        return True
    except Exception as e:
        print_fixed(f"加载模型失败: {str(e)}")
        traceback.print_exc()
        return False

# 获取自定义输入，与vanna_interactive.py中一致
def get_input_fixed():
    """获取用户输入的改进版本，避免中文字符间的空格问题"""
    if IS_MACOS:
        # 在macOS上使用read，而不是input
        sys.stdout.write('> ')
        sys.stdout.flush()
        line = ''
        while True:
            char = sys.stdin.read(1)
            if char == '\n':
                break
            line += char
        return line.strip()
    else:
        # 在其他平台上使用正常的input
        return input().strip()

# 交互式问答模式
def interactive_mode():
    """进入交互式问答模式"""
    print_fixed("进入交互式问答模式 (输入 'exit' 退出)")
    while True:
        question = get_input_fixed()
        if question.lower() in ['exit', 'quit', '退出']:
            break
        ask_question(question)

# 命令行界面
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print_fixed("用法:")
        print_fixed("  训练DDL文件:      python vanna_local.py train_ddl_file <ddl文件路径>")
        print_fixed("  训练DDL文本:      python vanna_local.py train_ddl \"CREATE TABLE...\"")
        print_fixed("  训练SQL文件:      python vanna_local.py train_sql_file <sql文件路径>")
        print_fixed("  训练SQL文本:      python vanna_local.py train_sql \"SELECT...\"")
        print_fixed("  训练文档文件:     python vanna_local.py train_doc_file <doc文件路径>")
        print_fixed("  训练文档文本:     python vanna_local.py train_doc \"业务说明...\"")
        print_fixed("  训练问题SQL对:    python vanna_local.py train_qsql \"问题\" \"SELECT...\"")
        print_fixed("  训练问题SQL文件:  python vanna_local.py train_qsql_file <文件路径>")
        print_fixed("  提问:            python vanna_local.py ask \"你的问题\"")
        print_fixed("  完整问答:        python vanna_local.py ask_full \"你的问题\"")
        print_fixed("  交互模式:        python vanna_local.py interactive")
        print_fixed("  保存模型:        python vanna_local.py save [文件名]")
        print_fixed("  加载模型:        python vanna_local.py load [文件名]")
        print_fixed("  数据分析:        python vanna_local.py analyze \"原始问题\" \"SQL\" \"数据文件路径\" \"分析问题\"")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "train_ddl_file" and len(sys.argv) > 2:
        train_with_ddl(ddl_file=sys.argv[2])
    elif command == "train_ddl" and len(sys.argv) > 2:
        train_with_ddl(ddl_text=sys.argv[2])
    elif command == "train_sql_file" and len(sys.argv) > 2:
        train_with_sql(sql_file=sys.argv[2])
    elif command == "train_sql" and len(sys.argv) > 2:
        train_with_sql(sql_text=sys.argv[2])
    elif command == "train_doc_file" and len(sys.argv) > 2:
        train_with_doc(doc_file=sys.argv[2])
    elif command == "train_doc" and len(sys.argv) > 2:
        train_with_doc(doc_text=sys.argv[2])
    elif command == "train_qsql" and len(sys.argv) > 3:
        train_with_question_sql(question=sys.argv[2], sql=sys.argv[3])
    elif command == "train_qsql_file" and len(sys.argv) > 2:
        train_with_question_sql(file=sys.argv[2])
    elif command == "ask" and len(sys.argv) > 2:
        ask_question(sys.argv[2])
    elif command == "ask_full" and len(sys.argv) > 2:
        ask_full(sys.argv[2])
    elif command == "interactive":
        interactive_mode()
    elif command == "save":
        filename = sys.argv[2] if len(sys.argv) > 2 else "vanna_model"
        save_database(filename)
    elif command == "load":
        filename = sys.argv[2] if len(sys.argv) > 2 else "vanna_model"
        load_model(filename)
    elif command == "analyze" and len(sys.argv) > 5:
        # 处理数据分析命令
        original_question = sys.argv[2]
        sql = sys.argv[3]
        data_file = sys.argv[4]
        analysis_question = sys.argv[5]
        
        try:
            # 读取数据文件
            if data_file.endswith('.csv'):
                data = pd.read_csv(data_file)
            elif data_file.endswith('.json'):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # 尝试推断文件类型
                try:
                    data = pd.read_csv(data_file)
                except:
                    try:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = f.read()
            
            # 调用分析函数
            result = analyze_data_with_ai(original_question, sql, data, analysis_question)
            print_fixed("\n分析结果:")
            print_fixed(result)
        except Exception as e:
            print_fixed(f"分析数据时出错: {str(e)}")
            traceback.print_exc()
    else:
        print_fixed("无效的命令或参数不足")