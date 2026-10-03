import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from models.schema import ETLAgentSchema
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

# ----------------------------------------------- ETL Agent ------------------------------------------

@tool
def extract_load_tool(url:str, output_folder: str, format:str) -> str:
    """
            This tool extract the data from the API (url) and loads it into the 
            desired location (destination)
            
            Args: 
                url (str): The API Endpoint from which to extract data.
                output_folder (str): The Folder Where The Extracted Data will be saved. 
            
            Returns:
                str: A Message That Indicating a sucess or failure of the operation.
    """
    etl_tool = ETLTools()
    return etl_tool.extract_load(url, output_folder, format)
    