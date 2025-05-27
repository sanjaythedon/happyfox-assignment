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


if __name__ == "__main__":
    # Example usage
    db = Database()
    print(f"Database created at: {db.db_path}")
    db.close()
