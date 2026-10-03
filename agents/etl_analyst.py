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

@tool
def transform_load_tool(input_file_path:str, output_folder:str, output_format:str) -> str:
    """
        This tool transform the data from the specified files and load it 
        into the desired locations (output_folder).
            
        Args:
            input_file_path (str): The path of the file containing the data to be transformed
            output_path (str): the folder where the transformed data will be saved    
            output_format (str): the format in which data will be saved (csv, json, parquet)    
                
        Returns:
            str: A message indicating the sucess or failure of the operation 
    """
    etl_tool = ETLTools()
    
    top_3_rows = etl_tool.transform_load_context(input_file_path, output_folder, output_format)
    
    llm = pick_llm("high")
    
    prompt =f"""
            you are a python data analyst who uses pandas to analyze data.
            you need to provide only the pandas code that will help to perform the right ETL operations
            as per the users question. Do not provide any explanation or comments, only
            the code should be provided. the code should be in a format that can be executed
            in a python enviorment with pandas installed. 
            Don't write anything else than pandas code. \n
            
            
            """
                   
    