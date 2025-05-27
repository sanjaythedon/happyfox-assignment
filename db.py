import sqlite3
import os
from pathlib import Path


class Database:
    def __init__(self, db_name="app.db", db_path=None):
        """
        Initialize the Database class.
        """
        self.db_name = db_name
        
        if db_path:
            Path(db_path).mkdir(parents=True, exist_ok=True)
            self.db_path = os.path.join(db_path, db_name)
        else:
            self.db_path = db_name
            
        self.connection = None
        self.cursor = None
        
        self.connect()
        
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def __del__(self):
        self.close()


    def create_table(self, table_name, columns):
        """
        Create a table in the database.
        
        Args:
            table_name (str): Name of the table to create
            columns (dict): Dictionary with column names as keys and data types as values
                           Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}
        
        Returns:
            bool: True if table creation is successful, False otherwise
        """
        try:
            # Construct the SQL query
            columns_str = ", ".join([f"{col_name} {data_type}" for col_name, data_type in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            
            # Execute the query
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")
            return False
            
    def insert(self, table_name, data):
        """
        Insert data into a table.
        
        """
        try:
            columns = list(data.keys())
            values = list(data.values())
            
            placeholders = ", ".join(["?" for _ in columns])
            
            columns_str = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting into table {table_name}: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    db = Database()
    
    # Example of creating a table
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    db.create_table("users", columns)
    print(f"Database created at: {db.db_path}")
    
    # Example of inserting data
    user1 = {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    user1_id = db.insert("users", user1)
    print(f"Inserted user with ID: {user1_id}")
    
    user2 = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
    }
    user2_id = db.insert("users", user2)
    print(f"Inserted user with ID: {user2_id}")
    
    # Close the database connection
    db.close()
