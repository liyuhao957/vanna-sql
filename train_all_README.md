# Vanna SQL 完整训练流程说明

这个文档解释如何使用`train_all.py`脚本执行Vanna SQL系统的完整训练流程。

## 脚本功能

`train_all.py`脚本按照官方推荐的最佳实践顺序，自动执行以下训练步骤：

1. **DDL（表结构）** - 从`XL/docs/table_docs/`目录加载所有SQL文件
2. **业务文档/解释** - 从`XL/docs/attribute_docs/`和`XL/docs/business_docs/`目录加载所有TXT文件
3. **SQL示例（常用查询）** - 从`XL/examples/sql_examples/`目录加载所有SQL和TXT文件
4. **问题-SQL对** - 从`XL/train/all_training_pairs.json`加载所有问题-SQL对

## 使用前准备

1. 确保已安装必要的依赖：

```bash
pip install vanna tqdm
```

2. 确保您的目录结构符合上述路径要求，或根据实际情况修改脚本中的路径。

## 使用方法

1. 运行优化脚本（可选，如果您还没有生成标准化的问题-SQL对）：

```bash
python optimize_training_data.py
```

2. 运行完整训练流程：

```bash
python train_all.py
```

3. 查看训练日志：
   - 控制台会实时显示训练进度
   - 详细日志保存在`vanna_training.log`文件中

## 注意事项

- 训练过程会按照官方推荐的顺序进行，这样能获得最佳效果
- 脚本会自动处理各种格式的文件，包括Markdown中的SQL代码块
- 大型文档会被自动分块处理，避免超出模型上下文限制
- 如果训练过程中出现错误，脚本会继续执行后续步骤，并将错误记录到日志中

## 训练完成后

训练完成后，您的Vanna模型将具备以下能力：

- 了解数据库表结构和字段信息
- 理解业务术语和领域知识
- 掌握常用SQL查询模式
- 能够根据自然语言问题生成对应的SQL查询

现在您可以使用Vanna生成SQL查询了！ 