import os

class ETLTools:
    
    def __init__(self):
        pass
    
    def extract_load(self, url:str, output_folder:str):
        """
        This tool extract the data from the API (url) and loads it into the 
        desired location (destination)
        
        Args: 
            url (str): The API Endpoint from which to extract data.
            output_folder (str): The Folder Where The Extracted Data will be saved. 
        
        Returns:
            str: A Message That Indicating a sucess or failure of the operation.
        """

