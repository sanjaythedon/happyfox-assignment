from abc import ABC, abstractmethod
from typing import Any


class FileReader(ABC):
    """Interface for reading from files."""
    
    @abstractmethod
    def read(self) -> Any:
        """Read data from a file."""
        pass


class FileWriter(ABC):
    """Interface for writing to files."""
    
    @abstractmethod
    def write(self, data: Any) -> bool:
        """Write data to a file."""
        pass