import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import HumanMessage, AIMessage

#--------------------------------------- AI Agent Code ------------------------------------

def curate_question(state:AgentSchema) -> AgentSchema:
    
    user_question = state.user_question

    llm = pick_llm("low")
    
    response = llm.invoke(f"create the following question : {user_question}").content
    
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
    
    state.prompt_query_context = prompt
    
    return state

#Generate SQL Query
def generate_sql(state: AgentSchema) -> AgentSchema:
    
    prompt = state.prompt_query_context
    
    llm = pick_llm("medium") 
        
    generated_sql_query = llm.invoke(prompt).content
        
    state.generated_sql_query = generated_sql_query  
    
    return state
        
#Is Safe Node
def is_safe_sql(state: AgentSchema)-> AgentSchema:
    sql_query = state.generated_sql_query
    
    llm = pick_llm("medium")
    llm_judge = llm.with_structured_output(JudgeSchema)
    
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

    response = llm_judge.invoke(prompt).model_dump()
    state.is_safe_sql_response = response['answer']
    state.comments = response['comments']
    
    return state
    
# Cancelled SQL Node    
def canceled_sql(state: AgentSchema) -> AgentSchema:
    
    comments = state.comments
    
    state.final_answer = f"The Generated SQL query was deemed unsafe to execute. the reason provided by the judge is: {comments}, Therefore the SQL query will not be executed"
    state.messages = state.messages + [AIMessage(content = f"{state.final_answer}")]
    
    return state

# Execute SQL query node
def execute_sql(state : AgentSchema) -> AgentSchema:
    
    sql_query = state.generated_sql_query
    
    conn_details = {
        "host": os.environ['host'],
        "port": os.environ['port'],
        "user": os.environ['user'],
        "password": os.environ['password'],
        "dbname": os.environ['dbname']
    }
    
    obj = DatabaseUtil(conn_details)
    
    execute_result = obj.execute_sql(sql_query)
    
    state.sql_query_execution_result = execution_result
    
    return state

# Represent the final answer Node
def represent_final_answer(state: AgentSchema) -> AgentSchema:
    
    execution_result = state.sql_query_execution_result
    curated_question = state.curated_question
    
    llm = pick_llm("low")
    
    prompt = f"""
    you are a SQL analyst agent. your task is to provide a final answer to the user based on the
    execution result of the SQL query and the user's original question. the final answer should be
    concise, clear, and directly address the user's query. avoid including any SQL code or technical 
    details in the final answer. the final answer should be in a user-friendly format that is easy to
    understand. if the execution result is empty or does not provide a clear answer to the user's question, 
    explain this in the final answer.\n
    here is the execution result: {execution_result} \n
    here's the user's original question: {curated_question}
    """
    
    llm_response = llm.invoke(prompt).content
    
    state.final_answer = llm_response
    state.messages = state.messages + [AIMessage(content = f"{llm_response}")]
    
    return state
