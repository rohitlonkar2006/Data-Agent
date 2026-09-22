import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import HumanMessage

llm = pick_llm("medium")
llm_judge = llm.with_structured_output(JudgeSchema)

sql_query = "SELECT *FROM users WHERE age > 30;"
prompt = f"""
You are a SQL Judge for data security. your task is to determine weather the SQL query is safe or not.
the SQL query should only be used for data retrieval and should not modify the database in any way.
Neither the SQL query nor the prompt should contains any SQL commands that can modify the database,
such as INSERT , UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or any other commands that can change
the structure or the content of the database. if the SQL query is safe, respond with 'Yes' otherwise 
respond with 'No'. Additionally provide comments regarding your decision.
here's the SQL query to evaluate:
{sql_query} 
"""

print(llm_judge.invoke(prompt))
