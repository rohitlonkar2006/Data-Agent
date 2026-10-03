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
def transform_load_tool(input_file_path:str, output_folder:str, output_format:str, user_question:str) -> str:
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
            You are a Python data analyst who uses pandas to perform ETL operations.

            Provide only valid, executable Python code using pandas. Do not provide explanations, comments, markdown, or any text outside the code.

            Create a pandas DataFrame by loading the data from:
            {input_file_path}

            Use the user's question to determine the required ETL transformations.

            User's question:
            {user_question}

            Data context (first 3 rows):
            {top_3_rows}

            Requirements:
            1. Load the input file into a pandas DataFrame.
            2. Perform the required transformations based on the user's question.
            3. Preserve the original data unless the requested transformation requires modifying it.
            4. Handle missing values, data types, duplicates, filtering, column transformations, aggregations, or other operations only when required by the user's question.
            5. Save the final transformed DataFrame to {output_folder}.
            6. Create the output folder if it does not exist.
            7. Save the result as `transformed_data.csv`.
            8. The code must be directly executable in a Python environment with pandas installed.
            9. Use only pandas and Python standard-library functionality.
            10. Do not invent columns, values, transformations, or assumptions that are not supported by the user's question or the provided data context.

            Return only the Python code.
            """
    response = llm.invoke(prompt).content
    
    pandas_code = response.strip().strip('```').strip().lstrip('python').strip()
    
    
    