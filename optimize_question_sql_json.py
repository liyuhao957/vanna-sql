#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化example_question_sql.json，去除解释类问题SQL字段中的无关内容，只保留注释。
"""
import json
import re

input_file = 'example_question_sql.json'
output_file = 'example_question_sql.json'  # 直接覆盖

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    sql = item.get('sql', '')
    # 判断是否为解释类（全是注释或大部分是注释）
    lines = sql.split('\n')
    comment_lines = [line for line in lines if line.strip().startswith('--')]
    # 如果注释行占比大于50%，认为是解释类
    if len(comment_lines) >= max(1, len(lines) // 2):
        # 只保留注释行，去掉后续的"## ..."等无关内容
        item['sql'] = '\n'.join([line for line in lines if line.strip().startswith('--')])

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"已优化并覆盖保存到 {output_file}") 