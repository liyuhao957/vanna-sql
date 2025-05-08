Generating SQL for Postgres using OpenAI, ChromaDB
This notebook runs through the process of using the vanna Python package to generate SQL using AI (RAG + LLMs) including connecting to a database and training. If you're not ready to train on your own database, you can still try it using a sample SQLite database.

Run Using Colab Open in GitHub

Which LLM do you want to use?
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
ChromaDB
Use ChromaDBs open-source vector database for free locally. No additional setup is necessary -- all database files will be created and stored locally.
Qdrant
Use Qdrants open-source vector database
Marqo
Use Marqo locally for free. Requires additional setup. Or use their hosted option.
Other VectorDB
Use any other vector database. Requires additional setup.
Setup
%pip install 'vanna[chromadb,openai,postgres]'
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
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
vn.connect_to_postgres(host='my-host', dbname='my-dbname', user='my-user', password='my-password', port='my-port')
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

from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()