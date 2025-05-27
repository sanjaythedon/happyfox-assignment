import json
import os
from typing import Any

from FileHandler.interfaces import FileReader


class JSONFileHandler(FileReader):
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