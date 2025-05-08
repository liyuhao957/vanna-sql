import os
import json
import re
import shutil
import datetime
from pathlib import Path

def extract_question_sql_pairs(file_path, is_markdown=False):
    """从问题-SQL对文件中提取标准化的对
    
    Args:
        file_path: 文件路径
        is_markdown: 是否为Markdown格式（针对不同文件格式）
    """
    pairs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 根据文件类型选择不同的正则模式
        if is_markdown:
            # 针对ad_metrics_docs.txt等文件，有标题和段落结构
            pattern = r"问题:\s*(.*?)\s*\nSQL:\s*(%%sql\s*\n)?(.*?)(?=\n\n|\n问题:|\n##|\Z)"
        else:
            # 针对question_sql_pairs.txt等标准格式
            pattern = r"问题:\s*(.*?)\s*\nSQL:\s*(%%sql\s*\n)?(.*?)(?=\n问题:|\Z)"
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            question = match[0].strip()
            sql = match[2].strip()
            # 删除SQL中的%%sql标记
            sql = re.sub(r'%%sql\s*\n?', '', sql)
            if question and sql:
                pairs.append({"question": question, "sql": sql})
        
        print(f"从 {file_path} 提取了 {len(pairs)} 个问题-SQL对")
    except Exception as e:
        print(f"处理 {file_path} 时发生错误: {e}")
    
    return pairs

def extract_sql_from_example(file_path):
    """从SQL示例文件提取问答对
    
    Args:
        file_path: SQL文件路径
    """
    pairs = []
    current_query = {"comments": [], "sql": []}
    in_query = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检测注释行
            if line_stripped.startswith('--') or line_stripped.startswith('#'):
                comment = line_stripped.lstrip('- #').strip()
                
                # 如果是新注释块的开始，保存上一个查询
                if not in_query and current_query["sql"] and current_query["comments"]:
                    # 从注释中提取可能的问题
                    question = " ".join(current_query["comments"])
                    sql = "\n".join(current_query["sql"])
                    if question and sql:
                        pairs.append({"question": question, "sql": sql})
                    current_query = {"comments": [], "sql": []}
                
                if comment:
                    current_query["comments"].append(comment)
                in_query = False
            
            # 检测SQL行
            elif line_stripped and not line_stripped.startswith('%%sql'):
                # 删除SQL中的%%sql标记
                if line_stripped == '%%sql':
                    continue
                
                current_query["sql"].append(line_stripped)
                in_query = True
        
        # 处理最后一个查询
        if current_query["sql"] and current_query["comments"]:
            question = " ".join(current_query["comments"])
            sql = "\n".join(current_query["sql"])
            if question and sql:
                pairs.append({"question": question, "sql": sql})
        
        print(f"从 {file_path} 提取了 {len(pairs)} 个SQL示例")
    except Exception as e:
        print(f"处理 {file_path} 时发生错误: {e}")
    
    return pairs

def extract_from_quickapp_structure(file_path):
    """从表结构SQL文件中提取表结构信息
    
    Args:
        file_path: 表结构SQL文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成一些基于表结构的问题-SQL对
        table_name_match = re.search(r'CREATE TABLE `([^`]+)`', content)
        if table_name_match:
            table_name = table_name_match.group(1)
            # 添加一些基本的表结构查询示例
            pairs = [
                {
                    "question": f"查询{table_name}表的所有字段",
                    "sql": f"SELECT * FROM {table_name} LIMIT 10;"
                },
                {
                    "question": f"统计{table_name}表的记录数",
                    "sql": f"SELECT COUNT(*) FROM {table_name};"
                }
            ]
            
            # 提取字段定义
            column_matches = re.findall(r'`([^`]+)`\s+([^,\n]+)[,\n]', content)
            fields = []
            for col_name, col_type in column_matches:
                # 清理列类型中的注释
                col_type_clean = re.sub(r'COMMENT\s+"[^"]*"', '', col_type).strip()
                fields.append((col_name, col_type_clean))
            
            if fields:
                field_list = ", ".join([f"`{field[0]}`" for field in fields[:5]])
                pairs.append({
                    "question": f"查询{table_name}表的前五个字段数据",
                    "sql": f"SELECT {field_list} FROM {table_name} LIMIT 10;"
                })
            
            print(f"从 {file_path} 生成了 {len(pairs)} 个基于表结构的查询示例")
            return pairs
    except Exception as e:
        print(f"处理 {file_path} 时发生错误: {e}")
    
    return []

def organize_files():
    """整理文件到相应目录"""
    try:
        # 复制文件到相应目录
        shutil.copy("XL/quickapp_table_structure.sql", "XL/docs/table_docs/")
        shutil.copy("XL/event_attribute_docs.txt", "XL/docs/attribute_docs/")
        shutil.copy("XL/ad_metrics_docs.txt", "XL/docs/business_docs/")
        shutil.copy("XL/app_packages.txt", "XL/docs/business_docs/")
        shutil.copy("XL/example_queries.sql", "XL/examples/sql_examples/")
        shutil.copy("XL/common_queries.txt", "XL/examples/sql_examples/")
        
        if os.path.exists("XL/sql_format_examples.txt"):
            shutil.copy("XL/sql_format_examples.txt", "XL/examples/best_practices/")
        if os.path.exists("XL/sql_template.txt"):
            shutil.copy("XL/sql_template.txt", "XL/examples/best_practices/")
        if os.path.exists("XL/starrocks_best_practices.txt"):
            shutil.copy("XL/starrocks_best_practices.txt", "XL/examples/best_practices/")
        if os.path.exists("XL/successful_queries.txt"):
            shutil.copy("XL/successful_queries.txt", "XL/logs/")
        if os.path.exists("XL/sql_fixes.txt"):
            shutil.copy("XL/sql_fixes.txt", "XL/logs/")
        
        print("文件整理完成")
    except Exception as e:
        print(f"整理文件时发生错误: {e}")

def main():
    """主处理函数"""
    all_pairs = []
    
    # 创建输出目录
    Path("XL/train").mkdir(parents=True, exist_ok=True)
    
    # 整理文件到相应目录
    organize_files()
    
    # 处理问题-SQL对文件
    if os.path.exists("XL/question_sql_pairs.txt"):
        pairs = extract_question_sql_pairs("XL/question_sql_pairs.txt")
        all_pairs.extend(pairs)
    
    # 处理广告指标文档
    if os.path.exists("XL/ad_metrics_docs.txt"):
        pairs = extract_question_sql_pairs("XL/ad_metrics_docs.txt", is_markdown=True)
        all_pairs.extend(pairs)
    
    # 处理SQL示例文件
    if os.path.exists("XL/example_queries.sql"):
        pairs = extract_sql_from_example("XL/example_queries.sql")
        all_pairs.extend(pairs)
    
    # 处理通用查询文件
    if os.path.exists("XL/common_queries.txt"):
        pairs = extract_question_sql_pairs("XL/common_queries.txt")
        all_pairs.extend(pairs)
    
    # 处理表结构文件
    if os.path.exists("XL/quickapp_table_structure.sql"):
        pairs = extract_from_quickapp_structure("XL/quickapp_table_structure.sql")
        all_pairs.extend(pairs)
    
    # 去重
    unique_pairs = []
    seen_questions = set()
    for pair in all_pairs:
        if pair["question"] not in seen_questions:
            seen_questions.add(pair["question"])
            unique_pairs.append(pair)
    
    # 输出标准化JSON
    output_path = "XL/train/all_training_pairs.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"已提取并标准化 {len(unique_pairs)} 个问题-SQL对，保存到 {output_path}")
    
    # 当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建一个训练数据README文件，说明数据来源和用途
    readme_content = f"""# 训练数据说明

本目录包含Vanna SQL系统的训练数据，由多个来源的SQL示例和问题-SQL对自动整合而成。

## 数据来源

- question_sql_pairs.txt: 标准问题-SQL对
- ad_metrics_docs.txt: 广告指标文档中的SQL示例
- example_queries.sql: SQL示例文件中的查询
- common_queries.txt: 常用查询模板
- quickapp_table_structure.sql: 表结构定义

## 数据统计

- 总问题-SQL对数量: {len(unique_pairs)}
- 去重前总数: {len(all_pairs)}

## 使用方法

使用以下命令训练Vanna模型:

```bash
vanna train --data {output_path}
```

最后更新时间: {current_time}
"""
    
    with open("XL/train/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("已创建训练数据README文件")

if __name__ == "__main__":
    main() 