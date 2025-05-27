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
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(f"File not found: {self._file_path}")
            
        try:
            with open(self._file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in file: {self._file_path}", e.doc, e.pos)