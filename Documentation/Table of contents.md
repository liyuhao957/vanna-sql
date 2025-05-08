Generating SQL for Other Database using OpenAI via Vanna.AI (Recommended), Vanna Hosted Vector DB (Recommended)
This notebook runs through the process of using the vanna Python package to generate SQL using AI (RAG + LLMs) including connecting to a database and training. If you're not ready to train on your own database, you can still try it using a sample SQLite database.

Run Using Colab Open in GitHub

Which LLM do you want to use?
OpenAI via Vanna.AI (Recommended)
Use Vanna.AI for free to generate your queries
OpenAI
Use OpenAI with your own API key
Azure OpenAI
If you have OpenAI models deployed on Azure
Anthropic
Use Anthropics Claude with your Anthropic API Key
Ollama
Use Ollama locally for free. Requires additional setup.
Google Gemini
Use Google Gemini with your Gemini or Vertex API Key
Mistral via Mistral API
If you have a Mistral API key
Other LLM
If you have a different LLM model
Where do you want to store the 'training' data?
Vanna Hosted Vector DB (Recommended)
Use Vanna.AIs hosted vector database (pgvector) for free. This is usable across machines with no additional setup.
ChromaDB
Use ChromaDBs open-source vector database for free locally. No additional setup is necessary -- all database files will be created and stored locally.
Qdrant
Use Qdrants open-source vector database
Marqo
Use Marqo locally for free. Requires additional setup. Or use their hosted option.
Other VectorDB
Use any other vector database. Requires additional setup.
Setup
%pip install vanna
import vanna
from vanna.remote import VannaDefault
api_key = # Your API key from https://vanna.ai/account/profile 

vanna_model_name = # Your model name from https://vanna.ai/account/profile 
vn = VannaDefault(model=vanna_model_name, api_key=api_key)
Which database do you want to query?
Postgres
Microsoft SQL Server
MySQL
DuckDB
Snowflake
BigQuery
SQLite
Oracle
Other Database
Use Vanna to generate queries for any SQL database
import pandas as pd

# There's usually a library for connecting to your type of database. Any SQL database will work here -- you just have to use the right library.
conn_details = {...}  # fill this with your connection details
conn = ...  # fill this with your connection object

# You define a function that takes in a SQL query as a string and returns a pandas dataframe
def run_sql(sql: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql, conn)
    return df

# This gives the package a function that it can use to run the SQL
vn.run_sql = run_sql
vn.run_sql_is_set = True
Training
You only need to train once. Do not train again unless you want to add more training data.

# The information schema query may need some tweaking depending on your database. This is a good starting point.
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)
plan

# If you like the plan, then uncomment this and run it to train
# vn.train(plan=plan)
# The following are methods for adding training data. Make sure you modify the examples to match your database.

# DDL statements are powerful because they specify table names, colume names, types, and potentially relationships
vn.train(ddl="""
    CREATE TABLE IF NOT EXISTS my-table (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
""")

# Sometimes you may want to add documentation about your business terminology or definitions.
vn.train(documentation="Our business defines OTIF score as the percentage of orders that are delivered on time and in full")

# You can also add SQL queries to your training data. This is useful if you have some queries already laying around. You can just copy and paste those from your editor to begin generating new SQL.
vn.train(sql="SELECT * FROM my-table WHERE name = 'John Doe'")
# At any time you can inspect what training data the package is able to reference
training_data = vn.get_training_data()
training_data
# You can remove training data if there's obsolete/incorrect information. 
vn.remove_training_data(id='1-ddl')

```## Asking the AI
Whenever you ask a new question, it will find the 10 most relevant pieces of training data and use it as part of the LLM prompt to generate the SQL.
```python
vn.ask(question=...)
Launch the User Interface
vanna-flask

