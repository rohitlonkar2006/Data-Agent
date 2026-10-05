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
            
            df = pd.json_normalize(data['results'])
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

    def transform_load_context(self, file_path:str):
        """
        This tool transform the data from the specified files and load it 
        into the desired locations (output_folder).
        
        Args:
            file_path (str): The path of the file containing the data to be transformed
            output_path (str): the folder where the transformed data will be saved    
            
        Returns:
            str: A message indicating the sucess or failure of the operation 
        """
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension == ".json":
            df = pd.read_json(file_path)
        elif file_extension == ".parquet":
            df = pd.read_parquet(file_path)
        else:
            return f"Unsupported File Format: {file_extension}"
        
        top_3_rows = str(df.head(3))
        
        return top_3_rows
    
    
    def execute_code(self, code:str):
        """
        This tool will execute the provided code and returns the output
        
        Args:
            code (str): The code to be executed 
        
        Returns
            str: The output of the executed code or an error message if execution fails.
        """
        try:
            exec(code)
            return "Code Executed Sucessfully."
        except Exception as e:
            return f"Failed To Execute the code: {e}"
        
        
if __name__ == "__main__":
    obj = ETLTools()
    path = "C:\\Users\\Samarth\\Desktop\\Projects\\Data-Agent\\data\\extract\\extracted_data.csv"
    print(obj.transform_load_content(path))