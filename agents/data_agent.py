import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from models.schema import RouterSchema, DataAgentSchema
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from etl_analyst import etl_analyst
from sql_analyst import final_graph
llm = pick_llm("high")

llm_router = llm.with_structured_output(RouterSchema)
# ---------------------------------------- DATA AGENT GRAPH ---------------------------------------

def router_node(state: DataAgentSchema):
    
    message = state.messages[-1]
    
    route_response_dict = llm_router.invoke(message).model_dump()
    
    route_response = route_response_dict['answer']
    
    state.route_response = route_response
    
def etl_node(state:DataAgentSchema):
    messages = state.messages[-1].content
    response = etl_analyst.invoke(
            {"messages" : [HumanMessage(content = f"""
            {messages}
            """)]}
        )
    state.messages = state.messages + [response]
    
def sql_node(state: DataAgentSchema):
    
    messages = state.messages[-1].content
    
    input_schema = {
            "messages":[],
            "user_question":f"{messages}",
            "curated_question":"",
            "prompt_query_context":"",
            "generated_sql_query":"",
            "is_safe_sql_response":"No",
            "comments":"",
            "sql_query_execution_result":"",
            "final_answer":""
        }
    response = final_graph.invoke(input_schema)
    
    state.messages = state.messages + [response]

if __name__ == "__main__":
    pass