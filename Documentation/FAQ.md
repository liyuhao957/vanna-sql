Frequently Asked Questions
Is this open-source?
Yes. This documentation refers to Vanna OSS, which is open-source. If you are looking for Vanna Cloud, our hosted version, please go to Vanna Cloud.

Can I run this "offline"?
Yes. You can use Vanna with Ollama, which allows you to run your LLM offline and for the vector store, you can use ChromaDB. If you're actually running on a machine without an internet connection (i.e. Airgapped), you may need to do some fiddling with ChromaDB to pre-download the weights for the embedding function. Likewise you may need to pre-download the weights for the LLM.

Can I use this with my SQL database?
Yes. Vanna works with any SQL database that you can connect to with Python (which should be all of them). Vanna contains a number of pre-built connectors that you can use to connect to your database in one-line of code but you can always customize the connection.

What's necessary for Vanna to query your database is just a function called vn.run_sql which takes in a SQL query and returns a pandas DataFrame. If you can write a function that does that, you can use Vanna with your database. Here's an example:

import pandas as pd
import psycopg2

def run_sql(sql):
    conn = psycopg2.connect(
        host="localhost",
        database="my_database",
        user="my_user",
        password="my_password"
    )
    return pd.read_sql(sql, conn)

vn.run_sql = run_sql
vn.run_sql_is_set = True
How do I customize the ChromaDB path?
You can pass a 'path' parameter in the config object:

from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)

vn = MyVanna(config={'path': '/path/to/chromadb'})
These are six FAQ questions I believe are very frequent and the original FAQ does not answer

vn.ask is too slow, It can't stop loading on notebook
There could be many reasons for this but these are the most common 1. Plotly is unable to generate a plot of your data, set pass parameter visualize=False 2. LLM could not be responding, if you're using your own local LLM please check your API 3. SQL engine might be exhausted, please check with your DB admin

How can I see my training data? How can I edit it?
Use vn.get_training_data() to see the dataframe of your training data. You can add training data whenever you run vn.ask or vn.generate_sql, withauto_train = True. You can remove training data using vn.remove_training_data(id='id of row in training data'). You can loop over all ids in vn.get_training data to remove all

Can I ask vanna to summarize the query results or use the results of the query to my liking?
In the latest update of Vanna, we added the functionality of additional LLM functions. You can see here link

How can connect my SQL DB to Vanna if, it is not one of those listed on the documentation
You can connect to them but you will need to implement the methods listed here

Vanna cannot stop training or doesn't train when I try to run the training plan?
There could be many reason's for this, these are the most common: 1) Your training data is larger than the context window of the model, try to truncate the plan or do one ddl statement at a time 2) Vanna takes the training plan in a specific format. Basically your plan dataframe must have all the columns in SELECT * FROM INFORMATION_SCHEMA.COLUMNS 3) There could be some corruption or unusual statements in the training plan

Whenever I do vn.ask() or vn.generate_sql() Vanna does not return anything just returns an error? Or Vanna returns gibberish statements with weird character strings.
These are probable causes for this: 1) Vanna has not been trained on sql statements 2) There is some corruption in the training data, for example it could be that there is some non-SQL statements added in the SQL training. There could be some examples with unintended characters, try removing some of the data or use vn.get_related_sql() or vn.get_related_ddl() to see which example in the training data is it referencing 3) LLMs can hallucinate, if the problem persist, please do try using a different LLM.