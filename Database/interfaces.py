from abc import ABC, abstractmethod


class Connection(ABC):
    """Interface for database connection management."""
    
    @abstractmethod
    def connect(self):
        """Connect to the database."""
        pass
    
    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass


class TableOperations(ABC):
    """Interface for table operations."""
    
    @abstractmethod
    def create_table(self, table_name, columns):
        """Create a table in the database."""
        pass


class DataOperationsWithoutDelete(ABC):
    """Interface for data operations."""
    
    @abstractmethod
    def insert(self, table_name, data):
        """Insert data into a table."""
        pass
    
    @abstractmethod
    def read(self, table_name, columns=None, condition=None, condition_values=None):
        """Read data from a table."""
        pass
    
    @abstractmethod
    def update(self, table_name, data, condition, condition_values):
        """Update data in a table."""
        pass


class Database(Connection, TableOperations, DataOperationsWithoutDelete):
    """Complete database interface combining all operations."""
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()