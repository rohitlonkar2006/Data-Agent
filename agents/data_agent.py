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

llm = pick_llm("high")

llm_router = llm.with_structured_output(RouterSchema)
# ---------------------------------------- DATA AGENT GRAPH ---------------------------------------

def router_node(state: DataAgentSchema):
    
    message = state.messages[-1]
    
    route_response_dict = llm_router.invoke(message).model_dump()
    
    