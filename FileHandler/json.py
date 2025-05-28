import json
import os
from typing import Any

from FileHandler.interfaces import FileReader, FileWriter


class JSONFileHandler(FileReader, FileWriter):
    """Handler for JSON files implementing both read and write operations."""
    
    def __init__(self, file_path: str):
        """
        Initialize the JSON file handler.
        
        Args:
            file_path: Path to the JSON file
        """
        self._file_path = file_path
    
    def read(self) -> Any:
        """
        Read and parse JSON data from the file.
        
        Returns:
            Parsed JSON data
            
        Raises:
            Exception: If an error occurs while reading the file
        """
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(f"File not found: {self._file_path}")
            
        try:
            with open(self._file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Error reading file: {self._file_path}")

    def write(self, data: Any) -> bool:
        """
        Write JSON data to the file.
        
        Args:
            data: Data to write to the file
            
        Returns:
            True if the write operation was successful, False otherwise
            
        Raises:
            Exception: If an error occurs while writing the file
        """
        try:
            with open(self._file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            raise Exception(f"Error writing file: {self._file_path}")