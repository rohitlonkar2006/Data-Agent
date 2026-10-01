import os
import requests
import pandas as pd

class ETLTools:
    
    def __init__(self):
        pass
    
    def extract_load(self, url:str, output_folder:str, format:str):
        """
        This tool extract the data from the API (url) and loads it into the 
        desired location (destination)
        
        Args: 
            url (str): The API Endpoint from which to extract data.
            output_folder (str): The Folder Where The Extracted Data will be saved. 
        
        Returns:
            str: A Message That Indicating a sucess or failure of the operation.
        """

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        output_folder = os.path.join(project_root, output_folder)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            filename = os.path.join(output_folder, f"extracted_data.{format}")
            os.makedirs(output_folder, exist_ok = True)
            
            df = pd.json_normalize(data)
            if format == "csv":
                df.to_csv(filename, index = False)
            elif format == "json":
                df.to_json(filename, orient= "records", lines = True)
            elif format == "parquet":
                df.to_parquet(filename, index = False)
            else:
                return f"Unsupported Format: {format}"
            
            return f"Data Sucessfully Extracted and saved to: {filename}"
        except requests.exceptions.RequestException as e:
            return f"Failed To Extract Data: {e}"

