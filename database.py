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


    def create_table(self, table_name, columns):
        """
        Create a table in the database.
        """
        try:
            columns_str = ", ".join([f"{col_name} {data_type}" for col_name, data_type in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")
            return False


if __name__ == "__main__":
    db = Database()
    
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    db.create_table("users", columns)
    print(f"Database created at: {db.db_path}")
