#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import json
import logging
import time
from tqdm import tqdm
from pathlib import Path

# 本地私有化Vanna初始化
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

from openai import OpenAI
client = OpenAI(
    api_key="xai-WvUhgZsGciGI1CKwiVnBnBVPzbNMRzXBPjr4rPa9Eq6Y524LowNPBikgmRfJKkNJefZY60f4fdzw5PJ7",
    base_url="https://api.x.ai/v1"
)

vn = MyVanna(config={
    'model': 'grok-3-beta',
    # 'path': 'your_chromadb_path',
})
vn.client = client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vanna_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train_all_documents():
    """递归训练所有.sql/.txt文档（去掉.md）"""
    logger.info("开始递归训练所有.sql/.txt文档...")
    # 递归查找所有文件
    file_patterns = ["XL/**/*.sql", "XL/**/*.txt"]
    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(pattern, recursive=True))
    # 排除all_training_pairs.json（单独处理）
    files = [f for f in files if not f.endswith("all_training_pairs.json")]
    logger.info(f"共找到 {len(files)} 个文档文件")
    trained_count = 0
    for file in tqdm(files, desc="训练文档"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 分块处理，防止超长
                chunk_size = 2000
                doc_chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                for chunk in doc_chunks:
                    vn.train(documentation=chunk)
                    time.sleep(0.5)  # 防止API请求过快
                trained_count += 1
        except Exception as e:
            logger.error(f"训练文档 {file} 时出错: {str(e)}")
    logger.info(f"文档训练完成: {trained_count}/{len(files)} 个文件")

def train_question_sql_pairs():
    """训练问题-SQL对"""
    logger.info("开始训练问题-SQL对...")
    json_file = "XL/train/all_training_pairs.json"
    if not os.path.exists(json_file):
        logger.warning(f"问题-SQL对文件 {json_file} 不存在，跳过此步骤")
        return
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            pairs = json.load(f)
        total_pairs = len(pairs)
        trained_count = 0
        logger.info(f"找到 {total_pairs} 个问题-SQL对")
        for pair in tqdm(pairs, desc="训练问题-SQL对"):
            question = pair.get("question", "").strip()
            sql = pair.get("sql", "").strip()
            if question and sql:
                vn.train(question=question, sql=sql)
                trained_count += 1
                time.sleep(0.5)
        logger.info(f"问题-SQL对训练完成: {trained_count}/{total_pairs} 个问答对")
    except Exception as e:
        logger.error(f"训练问题-SQL对时出错: {str(e)}")

def main():
    logger.info("===== Vanna SQL全量训练流程开始 =====")
    train_all_documents()
    train_question_sql_pairs()
    logger.info("===== Vanna SQL全量训练流程结束 =====")
    logger.info("全部训练完成！你的Vanna模型现在具备了更强大的SQL生成能力。")

if __name__ == "__main__":
    main()