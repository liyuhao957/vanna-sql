The Major Factor
The primary determinant of the output accuracy of the system is the quality of the training data. The most consequential training data is the known correct question to SQL pairs. This is a stylized diagram of what to expect:
https://vanna.ai/docs/img/accuracy-over-time.png
The reason for this is that the system uses a retrieval augmentation layer to generate SQL queries. This layer is trained on a reference corpus of question-SQL pairs. The more question-SQL pairs that are known to be correct, the more accurate the system will be.

Question to SQL pairs contain a wealth of embedded information that the system can use to understand the context of the question. This is especially true when your users tend to ask questions that have a lot of ambiguity. The known correct SQL for a question actually encodes a lot of information:
https://vanna.ai/docs/img/anatomy-of-a-correct-answer.png
When a new question comes in, even very small LLMs can take the example correct answer and make slight alterations to the SQL to fit the new question. The closer the known correct SQL is to the new question, the more accurate the system will be. In the example above, if the user were to ask "What are the top 5 customers by sales?" virtually any LLM will be able to answer that question accurately.

Always start in a Jupyter notebook
When first using the system, we generally recommend using it within Jupyter so that you have maximum control over the training data that you're feeding it and can perform bulk operations like extracting your database schema, etc.

Nudges / Hints
When you're first getting up and running, try giving some "hints" about your preferences when asking a question. For example, if you're asking a question about a specific table, you might want to include the table name in your question. This will help the system understand the context of your question and provide a more accurate answer.

SQL Statements
SELECT * FROM my_table is a BAD example of a SQL statement to train the system with. It's too generic and doesn't provide enough context for the system to understand the structure of the table. If you use a SQL statement to train, it's best to use statements that use column names. For example, SELECT id, name, email FROM my_table is a better example of a SQL statement to train the system with.