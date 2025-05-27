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
    def fetch_emails(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """
        Fetch emails from the service.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Query string to filter emails
            
        Returns:
            List of email objects
        """
        pass
    
    @abstractmethod
    def get_email(self, email_id: str) -> Dict[str, Any]:
        """
        Get a specific email by ID.
        
        Args:
            email_id: ID of the email to retrieve
            
        Returns:
            Email object
        """
        pass
    
    @abstractmethod
    def update_email(self, message_id: str, **kwargs) -> bool:
        """
        Update an email's properties.
        
        Args:
            email_id: ID of the email to update
            **kwargs: Properties to update
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
