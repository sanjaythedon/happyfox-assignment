import sqlite3
from Database.interfaces import Database


class SQLiteConnection:
    """Handles SQLite connection management."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def get_connection(self):
        """Get the current connection."""
        return self.connection
    
    def get_cursor(self):
        """Get the current cursor."""
        return self.cursor
    
    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()
    
    def __del__(self):
        """Ensure connection is closed when object is destroyed."""
        self.close()


class SQLiteTableManager:
    """Handles SQLite table operations."""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    def create_table(self, table_name, columns):
        """
        Create a table in the database.
        
        Args:
            table_name: Name of the table to create
            columns: Dictionary of column names and data types
        
        Returns:
            True if table was created successfully, False otherwise
        """
        try:
            cursor = self.connection_manager.get_cursor()
            if not cursor:
                return False
                
            columns_str = ", ".join([f"{col_name} {data_type}" for col_name, data_type in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            
            cursor.execute(query)
            self.connection_manager.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")
            return False


class SQLiteDataManager:
    """Handles SQLite data operations."""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    def insert(self, table_name, data):
        """
        Insert data into a table.
        
        Args:
            table_name: Name of the table to insert data into
            data: Dictionary of column names and values to insert
        
        Returns:
            ID of the inserted row, or None if insertion failed
        """
        try:
            cursor = self.connection_manager.get_cursor()
            if not cursor:
                return None
                
            columns = list(data.keys())
            values = list(data.values())
            
            placeholders = ", ".join(["?" for _ in columns])
            
            columns_str = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            self.connection_manager.commit()
            
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting into table {table_name}: {e}")
            return None
    
    def read(self, table_name, columns=None, condition=None, condition_values=None):
        """
        Read data from a table.
        
        Args:
            table_name: Name of the table to read data from
            columns: List of column names to select, or None to select all columns
            condition: SQL condition to filter rows, or None to select all rows
            condition_values: Values to use in the condition, or None if no condition is specified
        
        Returns:
            List of dictionaries containing the selected data
        """
        try:
            cursor = self.connection_manager.get_cursor()
            if not cursor:
                return []
                
            if columns:
                columns_str = ", ".join(columns)
            else:
                columns_str = "*"
            query = f"SELECT {columns_str} FROM {table_name}"
            
            if condition:
                query += f" WHERE {condition}"
                
            if condition_values:
                cursor.execute(query, condition_values)
            else:
                cursor.execute(query)
                
            results = cursor.fetchall()
            
            if columns:
                column_names = columns
            else:
                column_names = [description[0] for description in cursor.description]
                
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
    
    def update(self, table_name, data, condition, condition_values):
        """
        Update data in a table.
        
        Args:
            table_name: Name of the table to update data in
            data: Dictionary of column names and values to update
            condition: SQL condition to filter rows to update
            condition_values: Values to use in the condition
        
        Returns:
            Number of rows updated
        """
        try:
            cursor = self.connection_manager.get_cursor()
            if not cursor:
                return 0
                
            set_clause = ", ".join([f"{column} = ?" for column in data.keys()])
            
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            
            values = list(data.values()) + list(condition_values)
            
            cursor.execute(query, values)
            self.connection_manager.commit()
            
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error updating table {table_name}: {e}")
            return 0


class SQLiteDatabase(Database):
    """SQLite database implementation using composition of specialized components."""
    
    def __init__(self, connection_manager=None, 
                 table_manager=None, data_manager=None):
        """Initialize the SQLiteDatabase.
        
        Args:
            connection_manager (SQLiteConnection, optional): Custom connection manager
            table_manager (SQLiteTableManager, optional): Custom table manager
            data_manager (SQLiteDataManager, optional): Custom data manager
        """
        
        self.connection_manager = connection_manager
        self.table_manager = table_manager
        self.data_manager = data_manager
        
        self.connect()
    
    def connect(self):
        """Connect to the database."""
        return self.connection_manager.connect()
    
    def close(self):
        """Close the database connection."""
        self.connection_manager.close()
    
    def create_table(self, table_name, columns):
        """Create a table in the database."""
        return self.table_manager.create_table(table_name, columns)
    
    def insert(self, table_name, data):
        """Insert data into a table."""
        return self.data_manager.insert(table_name, data)
    
    def read(self, table_name, columns=None, condition=None, condition_values=None):
        """Read data from a table."""
        return self.data_manager.read(table_name, columns, condition, condition_values)
    
    def update(self, table_name, data, condition, condition_values):
        """Update data in a table."""
        return self.data_manager.update(table_name, data, condition, condition_values)


if __name__ == "__main__":
    connection_manager = SQLiteConnection("app.db")
    db = SQLiteDatabase(
        connection_manager=connection_manager,
        table_manager=SQLiteTableManager(connection_manager),
        data_manager=SQLiteDataManager(connection_manager)
    )
    
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    db.create_table("users", columns)
    
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
    
    update_data = {
        "email": "john.updated@example.com"
    }
    rows_affected = db.update("users", update_data, "name = ?", ("John Doe",))
    print(f"\nUpdated {rows_affected} row(s)")
    
    updated_user = db.read("users", condition="name = ?", condition_values=("John Doe",))
    print("\nAfter update:")
    for user in updated_user:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
