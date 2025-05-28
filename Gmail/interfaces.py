from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class EmailAuthenticator(ABC):
    """Interface for email authentication."""
    
    @abstractmethod
    def authenticate(self) -> Any:
        """Authenticate with the email service."""
        pass


class EmailService(ABC):
    """Interface for email service operations."""
    
    @abstractmethod
    def fetch_emails(self, max_results: int, query: str = "") -> List[Dict[str, Any]]:
        """
        Fetch emails from the service.
        """
        pass
    
    @abstractmethod
    def get_email(self, email_id: str) -> Dict[str, Any]:
        """
        Get a specific email by ID.
        """
        pass
    
    @abstractmethod
    def update_email(self, message_id: str, **kwargs) -> bool:
        """
        Update an email's properties.
        """
        pass
