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
            
    def read(self, table_name, columns=None, condition=None, condition_values=None):
        """
        Read data from a table.
        """
        try:
            if columns:
                columns_str = ", ".join(columns)
            else:
                columns_str = "*"
            query = f"SELECT {columns_str} FROM {table_name}"
            
            if condition:
                query += f" WHERE {condition}"
                
            if condition_values:
                self.cursor.execute(query, condition_values)
            else:
                self.cursor.execute(query)
                
            results = self.cursor.fetchall()
            
            if columns:
                column_names = columns
            else:
                column_names = [description[0] for description in self.cursor.description]
                
            formatted_results = []
            for row in results:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[column_names[i]] = value
                formatted_results.append(row_dict)
                
            return formatted_results
        except sqlite3.Error as e:
            print(f"Error reading from table {table_name}: {e}")
            return []


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
    
    all_users = db.read("users")
    print("\nAll users:")
    for user in all_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    
    names_only = db.read("users", columns=["id", "name"])
    print("\nNames only:")
    for user in names_only:
        print(f"ID: {user['id']}, Name: {user['name']}")
    
    filtered_users = db.read("users", condition="name = ?", condition_values=("John Doe",))
    print("\nFiltered users:")
    for user in filtered_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    
    db.close()
