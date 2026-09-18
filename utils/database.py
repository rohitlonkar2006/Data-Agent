import psycopg2

class DatabaseUtil:
    def __init__(self, db_config):
        self.db_config=db_config
        
        try:
            self.connection = psycopg2.connect(**db_config)
            
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None
    def schema_details(self, schema_name):
        