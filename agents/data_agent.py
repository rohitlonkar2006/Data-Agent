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
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import final_graph
llm = pick_llm("high")

llm_router = llm.with_structured_output(RouterSchema)
# ---------------------------------------- DATA AGENT GRAPH ---------------------------------------

def router_node(state: DataAgentSchema):
    
    message = state.messages[-1]
    
    router_prompt = SystemMessage(
        content=(
            "You are a request router, not a task executor. Classify the user's request "
            "as 'etl' when it asks to extract, transform, or load data, and as 'sql' "
            "when it asks a question about data already in the database. Do not answer "
            "the request or generate code. Return only the RouterSchema fields."
        )
    )
    route_response_dict = llm_router.invoke([router_prompt, message]).model_dump()
    
    route_response = route_response_dict['answer']
    
    state.route_response = route_response
    
    return state
    
def etl_node(state:DataAgentSchema):
    messages = state.messages[-1].content
    response = etl_analyst.invoke(
            {"messages" : [HumanMessage(content = f"""
            {messages}
            """)]}
        )
    state.messages = state.messages + [response]
    
    return state
    
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
    
    return state

data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node("router_node",router_node)
data_agent_graph.add_node("etl_node",etl_node)
data_agent_graph.add_node("sql_node",sql_node)

data_agent_graph.add_edge(START, "router_node")

def route_edge(state:DataAgentSchema) -> str:
    if state.route_response == "sql":
        return "sql_node"
    elif state.route_response == "etl":
        return "etl_node"
    else:
        raise ValueError(f"Invalid route response: {state.route_response}")

data_agent_graph.add_conditional_edges("router_node",route_edge,{
    "sql_node":"sql_node",
    "etl_node":"etl_node"
})        

data_agent = data_agent_graph.compile()

from IPython.display import Image, display

img = Image(data_agent.get_graph().draw_mermaid_png())
with open("data_agent_graph.png","wb") as f:
    f.write(img.data)

if __name__ == "__main__":
    response = data_agent.invoke(
        {"messages":[HumanMessage(content = f"extract the data from 'https://pokeapi.co/api/v2/pokemon' and load in the data/extract folder ")],
         "route_response" : ""
         })
    
    print(response)