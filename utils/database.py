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
        
        schema_info_context = ""
        
        connection = self.connection
        cursor = connection.cursor()
        
        schema_info_context = f"Database Schema: {schema_name}\n"
        
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s;", (schema_name))
        tables_list = cursor.fetchall()
        
        for table in tables_list:
            table_name = table[0]
            schema_info_context = f"{schema_info_context}\nTable: {table_name}\n"
            
            cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;",(table_name))
            columns_list = cursor.fetchall()

            for column in columns_list:
                column_name = column[0]
                data_type = column[1]
                schema_info_context = f"{schema_info_context} Column: {column_name}, Data Type: {data_type}\n"
                
        return schema_info_context
    