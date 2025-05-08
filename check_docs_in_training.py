# -*- coding: utf-8 -*-
"""
检测指定文档内容是否已被Vanna SQL训练入库
"""

from main import vn  # 直接复用main.py里的vn对象

# 获取所有训练数据
df = vn.get_training_data()

# 定义每个文档的独特内容片段（建议用首行或独特段落）
doc_keywords = {
    "event_attribute_docs.txt": "事件和属性绑定关系说明",
    "ad_metrics_docs.txt": "广告指标分析文档",
    "app_packages.txt": "应用包名对应关系文档",
    "quickapp_table_structure.sql": "CREATE TABLE `ods_RealTime_pcc_quickapp_events`",
    "sql_format_examples.txt": "SQL查询格式规范",
    "sql_template.txt": "SQL查询模板 - 必须严格遵循",
    "starrocks_best_practices.txt": "StarRocks 数据库最佳实践",
    "common_queries.txt": "常用SQL查询模板",
    "example_queries.sql": "-- Query config events",
    "all_training_pairs.json": "统计过去30天内各类事件的数量分布"
}

print("检测结果：")
for doc, keyword in doc_keywords.items():
    found = (
        ('content' in df and df['content'].str.contains(keyword, na=False).any()) or
        ('question' in df and df['question'].str.contains(keyword, na=False).any()) or
        ('sql' in df and df['sql'].str.contains(keyword, na=False).any())
    )
    print(f"{doc}: {'已训练' if found else '未训练'}")