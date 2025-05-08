#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import json
from vanna_local import MyVanna, client, save_database

def print_red(text):
    """打印红色文字"""
    print(f"\033[91m{text}\033[0m")

def print_green(text):
    """打印绿色文字"""
    print(f"\033[92m{text}\033[0m")

def print_yellow(text):
    """打印黄色文字"""
    print(f"\033[93m{text}\033[0m")

def print_blue(text):
    """打印蓝色文字"""
    print(f"\033[94m{text}\033[0m")

def train_documents(vanna_obj, doc_files):
    """训练文档文件"""
    print_blue("\n训练文档文件:")
    print_blue("===========")
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            print_yellow(f"正在训练文档: {doc_file}")
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc_text = f.read()
                vanna_obj.train(documentation=doc_text)
                print_green(f"✓ 文档 {doc_file} 训练成功")
            except Exception as e:
                print_red(f"× 文档 {doc_file} 训练失败: {str(e)}")
        else:
            print_red(f"× 文件不存在: {doc_file}")
    
    return True

def train_sql_examples(vanna_obj, sql_files):
    """训练SQL示例文件"""
    print_blue("\n训练SQL示例:")
    print_blue("===========")
    
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            print_yellow(f"正在训练SQL文件: {sql_file}")
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_text = f.read()
                vanna_obj.train(sql=sql_text)
                print_green(f"✓ SQL文件 {sql_file} 训练成功")
            except Exception as e:
                print_red(f"× SQL文件 {sql_file} 训练失败: {str(e)}")
        else:
            print_red(f"× 文件不存在: {sql_file}")
    
    return True

def train_with_knowledge_base(vanna_obj):
    """从提示词知识库训练专业术语"""
    print_blue("\n训练提示词知识库:")
    print_blue("==============")
    
    # 尝试读取提示词知识库文件
    kb_paths = ["prompt/knowledge_base.json", "prompt/prompt/knowledge_base.json"]
    kb_loaded = False
    
    for kb_path in kb_paths:
        if os.path.exists(kb_path):
            print_yellow(f"正在从 {kb_path} 加载知识库")
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
                
                # 训练关键词
                keyword_count = 0
                for keyword, explanation in kb.get("keywords", {}).items():
                    doc_text = f"# 专业术语解释\n\n术语: {keyword}\n解释: {explanation}\n\n这个术语在SQL查询中可能会出现，应该按照上述解释处理。"
                    vanna_obj.train(documentation=doc_text)
                    keyword_count += 1
                    print_yellow(f"  - 已训练术语: {keyword}")
                
                # 训练不明确术语
                unclear_count = 0
                for term, explanation in kb.get("unclear_terms", {}).items():
                    doc_text = f"# 模糊术语说明\n\n术语: {term}\n说明: {explanation}\n\n这是一个可能引起歧义的术语，处理时应注意以上说明。"
                    vanna_obj.train(documentation=doc_text)
                    unclear_count += 1
                    print_yellow(f"  - 已训练模糊术语: {term}")
                
                total_terms = keyword_count + unclear_count
                if total_terms > 0:
                    print_green(f"✓ 知识库训练成功，共 {total_terms} 个术语 (关键词: {keyword_count}, 模糊术语: {unclear_count})")
                    kb_loaded = True
                else:
                    print_yellow(f"! 知识库 {kb_path} 中没有术语需要训练")
                
                break  # 成功读取一个知识库后就不再尝试其他路径
            except Exception as e:
                print_red(f"× 知识库 {kb_path} 训练失败: {str(e)}")
    
    if not kb_loaded:
        print_yellow("! 未找到可用的知识库文件或知识库为空")
    
    return kb_loaded

def train_question_sql_pairs(vanna_obj, pair_files):
    """训练问题-SQL对文件"""
    print_blue("\n训练问题-SQL对:")
    print_blue("=============")
    
    for pair_file in pair_files:
        if os.path.exists(pair_file):
            print_yellow(f"正在训练问题-SQL对文件: {pair_file}")
            try:
                # 从文件中读取问题-SQL对
                pairs = []
                current_question = None
                current_sql = ""
                
                with open(pair_file, 'r', encoding='utf-8') as f:
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
                    print_red(f"× 未在 {pair_file} 中找到有效的问题-SQL对")
                    continue
                
                for q, s in pairs:
                    vanna_obj.train(question=q, sql=s)
                    print_yellow(f"  - 训练问题: {q[:50]}...")
                
                print_green(f"✓ 问题-SQL对文件 {pair_file} 训练成功 ({len(pairs)} 个对)")
            except Exception as e:
                print_red(f"× 问题-SQL对文件 {pair_file} 训练失败: {str(e)}")
        else:
            print_red(f"× 文件不存在: {pair_file}")
    
    return True

def train_ddl_files(vanna_obj, ddl_files):
    """训练DDL文件"""
    print_blue("\n训练数据库结构(DDL):")
    print_blue("================")
    
    for ddl_file in ddl_files:
        if os.path.exists(ddl_file):
            print_yellow(f"正在训练DDL文件: {ddl_file}")
            try:
                with open(ddl_file, 'r', encoding='utf-8') as f:
                    ddl_text = f.read()
                vanna_obj.train(ddl=ddl_text)
                print_green(f"✓ DDL文件 {ddl_file} 训练成功")
            except Exception as e:
                print_red(f"× DDL文件 {ddl_file} 训练失败: {str(e)}")
        else:
            print_red(f"× 文件不存在: {ddl_file}")
    
    return True

def save_vanna_model(vanna_obj=None, should_save=True, model_name=None):
    """保存训练模型"""
    if not should_save:
        return True
    
    print_blue("\n保存训练模型:")
    print_blue("===========")
    
    # 如果没有指定名称，使用时间戳
    if not model_name:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        model_name = f"vanna_model_{timestamp}"
    
    print_yellow(f"正在保存模型: {model_name}")
    try:
        save_database(model_name)
        print_green(f"✓ 模型保存成功: {model_name}")
        return True
    except Exception as e:
        print_red(f"× 模型保存失败: {str(e)}")
        return False

def train_all(doc_files=None, sql_files=None, pair_files=None, ddl_files=None, should_save=True):
    """一键训练所有文件"""
    print_blue("\nVanna 一键训练工具")
    print_blue("================\n")
    
    # 初始化Vanna实例 - 修复初始化问题
    try:
        # 正确初始化方式，与vanna_local.py一致
        vanna = MyVanna(config={'model': 'grok-3-beta'})
        vanna.client = client  # 使用vanna_local.py中已经初始化的client
        print_green("✓ 已初始化Vanna实例")
    except Exception as e:
        print_red(f"× 初始化Vanna实例失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 训练提示词知识库
    train_with_knowledge_base(vanna)
    
    # 训练文档
    if doc_files:
        train_documents(vanna, doc_files)
    
    # 训练SQL示例
    if sql_files:
        train_sql_examples(vanna, sql_files)
    
    # 训练问题-SQL对
    if pair_files:
        train_question_sql_pairs(vanna, pair_files)
    
    # 训练DDL文件
    if ddl_files:
        train_ddl_files(vanna, ddl_files)
    
    # 保存模型
    if should_save:
        save_vanna_model(vanna, should_save=True)
    
    print_green("\n✓ 所有训练任务已完成！")
    return True

def main():
    parser = argparse.ArgumentParser(description="Vanna一键训练工具")
    parser.add_argument("--docs", nargs="+", help="要训练的文档文件列表")
    parser.add_argument("--sql", nargs="+", help="要训练的SQL文件列表")
    parser.add_argument("--pairs", nargs="+", help="要训练的问题-SQL对文件列表")
    parser.add_argument("--ddl", nargs="+", help="要训练的DDL文件列表")
    parser.add_argument("--no-save", action="store_true", help="不保存模型")
    parser.add_argument("--auto", action="store_true", help="自动搜索并训练所有可能的文件")
    parser.add_argument("--kb-only", action="store_true", help="仅训练提示词知识库")
    
    args = parser.parse_args()
    
    # 如果仅训练知识库
    if args.kb_only:
        try:
            vanna = MyVanna(config={'model': 'grok-3-beta'})
            vanna.client = client
            print_green("✓ 已初始化Vanna实例")
            train_with_knowledge_base(vanna)
            if not args.no_save:
                save_vanna_model(vanna, should_save=True)
            print_green("\n✓ 知识库训练完成！")
            return
        except Exception as e:
            print_red(f"× 知识库训练失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return
    
    # 如果使用自动模式
    if args.auto:
        doc_files = []
        sql_files = []
        pair_files = []
        ddl_files = []
        
        # 搜索当前目录下的文件
        for file in os.listdir('.'):
            lower_file = file.lower()
            
            # 文档文件 - 更多关键词和模式
            if (lower_file.endswith('.txt') and 
                any(keyword in lower_file for keyword in ['doc', 'docs', 'practices', 'template', 
                                                        'guide', 'attribute', 'info', 'reference', 
                                                        'packages', 'format'])):
                doc_files.append(file)
            
            # SQL文件 - 扩展检测
            elif (lower_file.endswith('.sql') or 
                 (lower_file.endswith('.txt') and 
                  any(keyword in lower_file for keyword in ['sql', 'query', 'queries', 'example', 'format']))):
                # 如果文件名明确表示它是DDL
                if any(keyword in lower_file for keyword in ['structure', 'schema', 'ddl', 'table']):
                    ddl_files.append(file)
                else:
                    sql_files.append(file)
            
            # 问题-SQL对文件 - 扩展检测
            elif (lower_file.endswith('.txt') and 
                 any(keyword in lower_file for keyword in ['question', 'pair', 'qa']) and
                 any(keyword in lower_file for keyword in ['sql', 'query'])):
                pair_files.append(file)
            
            # 特殊文件处理 - 单独处理一些特殊的文件名
            elif lower_file in ['common_queries.txt', 'vivo_query_template.txt']:
                # 这些是既是文档又是SQL示例的文件
                doc_files.append(file)
                sql_files.append(file)
            
            # DDL文件 - 如果还有其他DDL文件没有被上面的规则检测到
            elif (lower_file.endswith('.sql') and 
                 any(keyword in lower_file for keyword in ['structure', 'schema', 'ddl', 'table'])):
                ddl_files.append(file)
        
        print_yellow("自动模式已选择以下文件:")
        if doc_files:
            print_yellow(f"文档文件: {', '.join(doc_files)}")
        if sql_files:
            print_yellow(f"SQL文件: {', '.join(sql_files)}")
        if pair_files:
            print_yellow(f"问题-SQL对文件: {', '.join(pair_files)}")
        if ddl_files:
            print_yellow(f"DDL文件: {', '.join(ddl_files)}")
        
        confirm = input("\n确认使用这些文件进行训练? (y/n): ").lower().strip()
        if confirm != 'y':
            print_yellow("已取消训练")
            return
    else:
        # 使用命令行参数指定的文件
        doc_files = args.docs
        sql_files = args.sql
        pair_files = args.pairs
        ddl_files = args.ddl
    
    # 检查是否至少有一个文件要训练或使用了kb-only模式
    if not any([doc_files, sql_files, pair_files, ddl_files]) and not args.kb_only:
        print_red("错误: 没有指定任何要训练的文件")
        parser.print_help()
        return
    
    train_all(
        doc_files=doc_files,
        sql_files=sql_files,
        pair_files=pair_files,
        ddl_files=ddl_files,
        should_save=not args.no_save
    )

if __name__ == "__main__":
    main() 