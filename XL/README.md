# XL目录数据整理与优化说明

本目录包含用于Vanna SQL系统训练和参考的各类数据文件，经过整理和优化后的目录结构更加清晰。

## 目录结构

```
XL/
  train/                    # 标准化训练数据
    all_training_pairs.json # 合并所有来源的问题-SQL对
    README.md               # 训练数据说明
  
  docs/                     # 参考文档
    table_docs/             # 表结构文档
      quickapp_table_structure.sql
    attribute_docs/         # 属性说明文档
      event_attribute_docs.txt
    business_docs/          # 业务逻辑文档
      ad_metrics_docs.txt
      app_packages.txt
  
  examples/                 # SQL示例
    sql_examples/           # 各类SQL示例
      example_queries.sql
      common_queries.txt
    best_practices/         # 最佳实践和模板
      sql_format_examples.txt
      sql_template.txt
      starrocks_best_practices.txt
  
  logs/                     # 日志和记录
    successful_queries.txt
    sql_fixes.txt
```

## 数据说明

### 训练数据

`train/all_training_pairs.json`是标准化的训练数据，包含了从以下来源提取的问题-SQL对：

- 问题-SQL对文件（question_sql_pairs.txt）
- 广告指标文档（ad_metrics_docs.txt）
- SQL示例文件（example_queries.sql）
- 常用查询模板（common_queries.txt）
- 表结构定义（quickapp_table_structure.sql）

所有问题-SQL对均已标准化为JSON格式：

```json
{
  "question": "问题描述",
  "sql": "对应SQL语句"
}
```

### 参考文档

参考文档保存在`docs/`目录下，包括：

- **表结构文档**：数据库表的DDL定义
- **属性说明文档**：字段、事件等属性的详细说明
- **业务逻辑文档**：业务流程、指标计算等说明

### SQL示例和最佳实践

SQL示例和最佳实践保存在`examples/`目录下，包括：

- **SQL示例**：各类查询SQL示例
- **最佳实践**：SQL编写规范、模板和最佳实践

## 使用方法

### 训练Vanna SQL系统

使用标准化的训练数据训练Vanna：

```bash
vanna train --data XL/train/all_training_pairs.json
```

### 优化和更新训练数据

使用提供的`optimize_training_data.py`脚本可以重新处理原始数据文件，更新训练数据：

```bash
python optimize_training_data.py
```

## 注意事项

1. 原始数据文件仍保留在XL目录下，可以随时参考
2. 每次修改或添加原始数据文件后，建议重新运行优化脚本更新训练数据
3. 训练数据已去重，以避免重复样本对模型训练的影响 