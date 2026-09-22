import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema
from langchain_core.messages import HumanMessage

#--------------------------------------- AI Agent Code ------------------------------------

def curate_question(state:AgentSchema) -> AgentSchema:
    
    user_question = state.user_question

    llm = pick_llm("low")
    
    response = llm.invoke(f"create the following question : {user_question}")
    
    state.curated_question = response
    state.messages = state.messages + [HumanMessage(content = f"{response}")]
    
    return state

def prompt_query_context(state : AgentSchema) -> AgentSchema:
    
    curated_question = state.curated_question
    
    conn_details = {
        "host": os.environ['host'],
        "port": os.environ['port'],
        "user": os.environ['user'],
        "password": os.environ['password'],
        "dbname": os.environ['database'],
    }
    obj = DatabaseUtil(conn_details)
    
    schema_info = obj.schema_details("public")
    
    prompt = f"""
    You are a SQL Analyst agent. your task is to convert the user's natural language
    query into postgres SQL query that can be executed on the database. you are provided
    with the user's original query and schema details of the database, including
    table name, column name, data types, and sample data for each table so that
    you can understand the structure of the database and generate an accurate SQL query.
    unless user explicitly asks for specific number of rows, always limit the output at 10 rows.
    Note - just generate the SQL query without any explanation or additional text because
    this query will be executed directly on the database. So,the output should be SQL 
    ready to be executed without any modifications 
    
    user's original query : {curated_question}
    
    Database Schema Details:
    {schema_info}
    
    """
        