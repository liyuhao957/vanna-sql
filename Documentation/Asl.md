vn.ask
vn.ask("What are the top 10 customers by sales?")
Remember  记住了啊

The system first needs training data before you can begin asking questions.
在使用之前，系统得先有训练数据，不然你想问啥都没门儿。

The ask function is intended to be a convenience method for use in Jupyter notebooks. You use this function to ask questions and it will run the following constituent functions:
这个 ask 功能就是专门为 Jupyter 笔记本设计的省事儿工具。你用它来提问，它会一口气跑完下面那一堆小功能，超级方便！

vn.generate_sql
vn.run_sql
vn.generate_plotly_code
vn.get_plotly_figure
Note

If you are using Vanna outside of the context of a Jupyter notebook, you will should call these functions individually instead of using vn.ask. Since vn.ask runs several functions and does not return until all the functions are complete, you will experience a delay when using vn.ask in a non-notebook context.
如果你不在 Jupyter 笔记本的环境里用 Vanna，那还是老老实实一个个调用那些功能吧，别用 vn.ask 。因为 vn.ask 会把好几个功能一起跑，等它们全搞定才给你结果，所以在非笔记本的环境里用 vn.ask 的话，你得耐心等着，有点小延迟。