# Vanna SQL系统

这是一个使用Vanna库构建的自然语言到SQL转换系统，可以帮助用户通过自然语言生成SQL查询。

## 目录结构

```
vanna-sql/
  ├── main.py               # 主程序入口
  ├── train_local_data.py   # 本地数据训练脚本
  ├── optimize_training_data.py  # 训练数据优化脚本
  ├── train_all.py          # 完整训练流程脚本（按官方推荐顺序）
  ├── XL/                  # 训练数据和参考文档
  │   ├── train/           # 标准化训练数据
  │   ├── docs/            # 参考文档
  │   ├── examples/        # SQL示例
  │   └── logs/            # 日志和记录
  └── frontend/            # 前端界面
```

## XL目录说明

XL目录包含用于训练Vanna SQL系统的数据和参考文档，经过整理和优化后的目录结构如下：

```
XL/
  train/                    # 标准化训练数据
    all_training_pairs.json # 合并所有来源的问题-SQL对
    README.md               # 训练数据说明
  
  docs/                     # 参考文档
    table_docs/             # 表结构文档
    attribute_docs/         # 属性说明文档
    business_docs/          # 业务逻辑文档
  
  examples/                 # SQL示例
    sql_examples/           # 各类SQL示例
    best_practices/         # 最佳实践和模板
  
  logs/                     # 日志和记录
```

详细说明请参考 [XL/README.md](XL/README.md)。

### 训练Vanna模型

我们提供了两种训练方式：

#### 1. 完整训练流程（推荐）

使用官方推荐的最佳实践顺序执行完整训练流程：

```bash
python train_all.py
```

这将按照以下顺序训练模型：
1. DDL（表结构）
2. 业务文档/解释
3. SQL示例（常用查询）
4. 问题-SQL对

详细说明请参考 [train_all_README.md](train_all_README.md)。

#### 2. 仅优化并训练问题-SQL对

如果只想使用标准化的问题-SQL对训练：

```bash
# 先优化数据
python optimize_training_data.py

# 然后训练
python -c "import vanna; vanna.train(data='XL/train/all_training_pairs.json')"
```

---

## 主要功能

- **自然语言生成SQL**：输入问题，自动生成SQL语句，支持一键复制
- **训练数据管理**：支持DDL、业务文档、示例SQL、问题-SQL对的训练，支持查看和删除训练数据
- **Web可视化界面**：无需命令行，操作简单，界面美观

---

## 安装与启动

### 1. 安装依赖

建议使用Python虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate  # Windows下为 venv\Scripts\activate
pip install fastapi uvicorn vanna chromadb openai python-multipart tqdm
```

### 2. API密钥与模型配置

✅ **已配置完成**：API密钥和模型（grok-3-beta）已经在代码中配置好，您不需要额外设置。

### 3. 启动后端服务

```bash
python main.py
```

### 4. 访问Web页面

浏览器打开：[http://localhost:8000/](http://localhost:8000/)

---

## Web端使用说明

### 1. 训练数据管理
- **DDL**：输入或粘贴数据库表结构（如CREATE TABLE语句）
- **业务文档**：输入业务术语、规则、说明等
- **示例SQL**：输入常用SQL查询
- **问题-SQL对**：输入自然语言问题及其标准SQL答案
- 点击"训练"按钮即可添加训练数据
- 点击"查看训练数据"可浏览所有已训练内容，并可删除

### 2. SQL生成
- 在右侧输入自然语言问题（如"查找销售额最高的客户"）
- 点击"生成SQL"
- 下方会显示生成的SQL语句，可一键复制

---

## 常见问题

1. **为什么生成SQL不准确？**
   - 请尽量提供详细、准确的DDL、业务文档和示例SQL，尤其是"问题-SQL对"训练效果最佳。
   - 使用`train_all.py`执行完整训练流程，按官方推荐顺序训练可显著提高准确率。
   - 如果仅想整理数据，可以运行`optimize_training_data.py`优化XL目录下的训练数据。
2. **如何清空所有训练数据？**
   - 逐条删除即可，后续可扩展批量删除功能。
3. **支持哪些数据库？**
   - 只要能用SQL描述结构的数据库都支持（如MySQL、PostgreSQL、SQL Server、Oracle等）。
4. **是否会直接操作我的数据库？**
   - 不会。系统只生成SQL，不会连接或操作您的数据库。
5. **如何更换模型或API Key？**
   - 直接修改`main.py`中的`API_KEY`和`MODEL_NAME`变量，重启服务即可。
6. **XL目录中的文件很杂乱，怎么办？**
   - 运行`python optimize_training_data.py`自动整理并优化所有训练文件。

---

## 文件说明

- `main.py`：FastAPI后端，负责AI逻辑、API接口和静态文件服务
- `train_local_data.py`：批量训练本地数据的脚本
- `optimize_training_data.py`：优化XL目录数据结构和训练文件
- `train_all.py`：完整训练流程脚本（按官方推荐顺序）
- `frontend/index.html`：Web主页面，所有操作都在这里完成
- `frontend/style.css`：页面美化样式
- `XL/`：训练数据和参考文档目录
- `venv/`：Python虚拟环境（建议使用）
- `README.md`：本说明文档

---

## 致谢

- 本项目基于 [Vanna](https://github.com/vanna-ai/vanna) 开发，感谢Vanna团队的优秀开源工作。
- 如有问题欢迎提issue或交流。

---

祝你用AI轻松玩转SQL！ 