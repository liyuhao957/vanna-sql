# 训练数据说明

本目录包含Vanna SQL系统的训练数据，由多个来源的SQL示例和问题-SQL对自动整合而成。

## 数据来源

- question_sql_pairs.txt: 标准问题-SQL对
- ad_metrics_docs.txt: 广告指标文档中的SQL示例
- example_queries.sql: SQL示例文件中的查询
- common_queries.txt: 常用查询模板
- quickapp_table_structure.sql: 表结构定义

## 数据统计

- 总问题-SQL对数量: 28
- 去重前总数: 28

## 使用方法

使用以下命令训练Vanna模型:

```bash
vanna train --data XL/train/all_training_pairs.json
```

最后更新时间: 2025-05-07 14:16:30
