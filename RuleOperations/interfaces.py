from abc import ABC, abstractmethod
from Gmail import GmailService


class EmailOperation(ABC):
    """
    Abstract base class for email operations.
    Strategy Pattern: Different operations can be implemented as strategies.
    """
    
    @abstractmethod
    def apply(self, email_id: str, gmail_service: GmailService) -> bool:
        """
        Apply the operation to an email.
        
        Args:
            email_id: ID of the email to apply the operation to
            gmail_service: Gmail service to use for applying the operation
            
        Returns:
            True if operation was applied successfully, False otherwise
        """
        pass


class MarkAsReadOperation(EmailOperation):
    """Operation to mark an email as read."""
    
    def apply(self, email_id: str, gmail_service: GmailService) -> bool:
        """Mark the email as read."""
        print(f"  - Marking email {email_id} as read")
        return gmail_service.update_email(message_id=email_id, mark_as_read=True)


class MoveToLabelOperation(EmailOperation):
    """Operation to move an email to a label."""
    
    def __init__(self, label: str):
        """
        Initialize with the destination label.
        
        Args:
            label: Label to move the email to
        """
        self.label = label.upper()
    
    def apply(self, email_id: str, gmail_service: GmailService) -> bool:
        """Move the email to the specified label."""
        print(f"  - Moving email {email_id} to label {self.label}")
        return gmail_service.update_email(message_id=email_id, move_to_label=self.label)
