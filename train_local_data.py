#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vanna数据训练脚本
该脚本自动读取本地文件并将其用于训练Vanna模型
"""

import os
import json
import glob
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

# 配置API密钥和模型（从main.py复制）
API_KEY = "xai-xnlRKbwpndPtsh8Tf30EGlCw8KSGEDGM2S90jBeuru7FNAp1kOD1gP9YqLIl5AIubyuPz5n4EF6xD0LU"
MODEL_NAME = "grok-3-beta"

# 定义可能的数据文件路径（支持多种文件命名方式）
DDL_FILES = ['example_ddl.sql', 'ddl.sql', 'schema.sql', '*.ddl', '*.sql']
DOC_FILES = ['example_documentation.txt', 'documentation.txt', 'business_terms.txt', 'terms.txt', '*.doc', '*.txt']
SQL_FILES = ['example_sql_queries.sql', 'queries.sql', 'examples.sql', 'sample_queries.sql', '*.example.sql']
Q_SQL_FILES = ['example_question_sql.json', 'questions.json', 'qa_pairs.json', '*.qa.json']

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

def find_files(patterns):
    """查找文件，支持通配符"""
    found_files = []
    for pattern in patterns:
        if '*' in pattern:
            found_files.extend(glob.glob(pattern))
        elif os.path.exists(pattern):
            found_files.append(pattern)
    return found_files

def train_ddl_files(vn, files):
    """训练DDL文件"""
    count = 0
    for file in files:
        try:
            print(f"正在训练DDL文件: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                ddl = f.read()
                if ddl.strip():
                    vn.train(ddl=ddl)
                    count += 1
        except Exception as e:
            print(f"训练DDL文件 {file} 失败: {e}")
    return count

def train_doc_files(vn, files):
    """训练业务文档文件"""
    count = 0
    for file in files:
        try:
            print(f"正在训练业务文档: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                doc = f.read()
                if doc.strip():
                    vn.train(documentation=doc)
                    count += 1
        except Exception as e:
            print(f"训练业务文档 {file} 失败: {e}")
    return count

def train_sql_files(vn, files):
    """训练SQL文件"""
    count = 0
    for file in files:
        try:
            print(f"正在训练SQL文件: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                sql = f.read()
                if sql.strip():
                    vn.train(sql=sql)
                    count += 1
        except Exception as e:
            print(f"训练SQL文件 {file} 失败: {e}")
    return count

def train_qa_pairs(vn, files):
    """训练问题-SQL对"""
    count = 0
    for file in files:
        try:
            print(f"正在训练问题-SQL对文件: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 支持多种JSON格式
                if isinstance(data, list):
                    # 格式1: [{"question": "...", "sql": "..."}, ...]
                    for item in data:
                        if 'question' in item and 'sql' in item:
                            vn.train(question=item['question'], sql=item['sql'])
                            count += 1
                elif isinstance(data, dict):
                    # 格式2: {"question1": "sql1", "question2": "sql2", ...}
                    for question, sql in data.items():
                        vn.train(question=question, sql=sql)
                        count += 1
        except Exception as e:
            print(f"训练问题-SQL对文件 {file} 失败: {e}")
    return count

def main():
    """主函数"""
    print("=" * 50)
    print("Vanna 自动训练脚本")
    print("=" * 50)
    
    # 初始化Vanna
    vn = MyVanna(config={
        'api_key': API_KEY,
        'model': MODEL_NAME,
        'collection_name': 'vanna_web_demo'
    })
    
    # 查找所有可能的数据文件
    ddl_files = find_files(DDL_FILES)
    doc_files = find_files(DOC_FILES)
    sql_files = find_files(SQL_FILES)
    qa_files = find_files(Q_SQL_FILES)
    
    # 显示找到的文件
    print("\n找到以下文件:")
    print(f"DDL文件: {ddl_files or '无'}")
    print(f"业务文档: {doc_files or '无'}")
    print(f"SQL示例: {sql_files or '无'}")
    print(f"问题-SQL对: {qa_files or '无'}")
    
    # 询问用户是否继续
    confirm = input("\n是否开始训练这些文件? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消训练。")
        return
    
    # 开始训练
    print("\n开始训练...")
    
    # 训练DDL
    ddl_count = train_ddl_files(vn, ddl_files)
    
    # 训练业务文档
    doc_count = train_doc_files(vn, doc_files)
    
    # 训练SQL示例
    sql_count = train_sql_files(vn, sql_files)
    
    # 训练问题-SQL对
    qa_count = train_qa_pairs(vn, qa_files)
    
    # 统计结果
    print("\n训练结束！")
    print(f"成功训练的DDL文件: {ddl_count}")
    print(f"成功训练的业务文档: {doc_count}")
    print(f"成功训练的SQL示例: {sql_count}")
    print(f"成功训练的问题-SQL对: {qa_count}")
    
    # 检查是否至少有一个成功
    if ddl_count + doc_count + sql_count + qa_count > 0:
        print("\n恭喜！Vanna模型训练成功，现在您可以尝试生成SQL查询了。")
    else:
        print("\n警告：没有成功训练任何数据。请检查文件是否存在或格式是否正确。")
    
    # 进一步操作指导
    print("\n接下来您可以:")
    print("1. 访问 http://localhost:5173 使用Web界面")
    print("2. 添加更多训练数据再次运行此脚本")
    print("3. 编写问题-SQL对文件进行针对性训练，提高生成质量")

if __name__ == "__main__":
    main() 