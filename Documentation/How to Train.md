vn.train
vn.train is a wrapper function that allows you to train the system (i.e. the retrieval augmentation layer that sits on top of the LLM). You can call it in these ways:

DDL statements
These statements give the system an understanding of what tables, columns, and data types are available.

vn.train(ddl="CREATE TABLE my_table (id INT, name TEXT)")
Documentation strings
These can be any abtirary documentation about your database, business, or industry that may be necessary for the LLM to understand how the context of a user's question.

vn.train(documentation="Our business defines XYZ as ABC")
SQL Statements
One of the most helpful things for the system to understand is the SQL queries that are commonly used in your organization. This will help the system understand the context of the questions that are being asked.

vn.train(sql="SELECT col1, col2, col3 FROM my_table")
Question-SQL Pairs
You can also train the system with question-SQL pairs. This is the most direct way to train the system and is the most helpful for the system to understand the context of the questions that are being asked.

vn.train(
    question="What is the average age of our customers?", 
    sql="SELECT AVG(age) FROM customers"
)
Question-SQL pairs contain a wealth of embedded information that the system can use to understand the context of the question. This is especially true when your users tend to ask questions that have a lot of ambiguity.

Training Plan
# The information schema query may need some tweaking depending on your database. This is a good starting point.
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)
plan

# If you like the plan, then uncomment this and run it to train
vn.train(plan=plan)
A training plan is basically just your database information schema broken up into bite-sized chunks that can be referenced by the LLM. This is a good way to train the system with a lot of data quickly.