Behavior Customization
All Vanna functions are inherited from the VannaBase class. This is an abstract base class that provides the basic functionality for all Vanna functions. Depending on the specifics of the configuration you choose, the implementations live within the classes that inherit from this base class.

You may choose to customize the behavior of Vanna by creating your own class that inherits directly from VannaBase or from one of the classes that inherit from it. This is useful if you want to change the behavior of a specific function or if you want to add new functionality.

Class Instantiation
This is an example of how the class is instantiated when configured to use the OpenAI API and the ChromaDB vector store.

To customize the specifics of the behavior, you can override any of the methods in the base classes when you're instantiating the MyVanna class.

from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
Overriding a Specific Function
Here's an example of how to override the is_sql_valid function.

from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def is_sql_valid(self, sql: str) -> bool:
        # Your implementation here

        return False

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})

# Example usage
is_valid = vn.is_sql_valid("SELECT user_name, user_email FROM users WHERE user_id = 123")
print(f"Is the SQL valid? {is_valid}")
Adding an Additional LLM-based Function
If you want to add a new function that uses the LLM, you can do so by adding a new method to the class. Let's say that you want to "explain" a SQL query. You can add a new method to the class that uses the LLM to generate an explanation for the SQL query.

from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def generate_query_explanation(self, sql: str):
        my_prompt = [
            self.system_message("You are a helpful assistant that will explain a SQL query"),
            self.user_message("Explain this SQL query: " + sql),
        ]

        return self.submit_prompt(prompt=my_prompt)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-3.5-turbo'})

vn.generate_query_explanation("SELECT user_name, user_email FROM users WHERE user_id = 123")
Output: 'This SQL query is selecting the user_name and user_email columns from the users table. It is specifying a condition using the WHERE clause, where the user_id column must equal 123. In other words, it is retrieving the user_name and user_email of the user whose user_id is 123.'