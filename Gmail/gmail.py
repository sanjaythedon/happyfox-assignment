import os
import pickle
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

from Gmail.email_service import EmailAuthenticator, EmailService
from utils import get_message_body


class GmailAuthenticator(EmailAuthenticator):
    """
    Handles authentication with Gmail API using OAuth2.
    """
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """
        Initialize the Gmail authenticator.
        
        Args:
            credentials_file: Path to the credentials.json file
            token_file: Path to store/retrieve the token.pickle file
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get credentials from .env if not provided
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        if not self.credentials_file:
            raise ValueError("Credentials file path not provided in arguments or .env file")
        
        # Default token file location if not specified
        if not self.token_file:
            self.token_file = 'token.pickle'
    
    def authenticate(self) -> Any:
        """
        Authenticate to Gmail API using OAuth2.
        
        Returns:
            The authenticated Gmail API service or None if authentication fails
        """
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials available, authenticate or refresh
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # If no refresh token available, run the flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            # Build the Gmail API service
            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None


class EmailParser:
    """
    Handles parsing of email content.
    """
    @staticmethod
    def parse_email(content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse email content into a structured format.
        
        Args:
            content: Raw email content from Gmail API
            
        Returns:
            Structured email data
        """
        try:
            headers = content['payload']['headers']
            email_id = content['id']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            body = get_message_body(content['payload'])
            
            return {
                'unique_id': email_id,
                'Subject': subject,
                'From': sender,
                'Date Received': date,
                'Message': body
            }
        except Exception as e:
            print(f"Error parsing email: {e}")
            return None


class GmailService(EmailService):
    """
    Gmail service implementation using the EmailService interface.
    """
    
    def __init__(self, authenticator: GmailAuthenticator):
        """
        Initialize the Gmail service.
        
        Args:
            authenticator: Gmail authenticator instance
        
        Raises:
            ValueError: If authentication fails
        """
        self.authenticator = authenticator
        self.service = self.authenticator.authenticate()
        self.parser = EmailParser()
        
        if not self.service:
            raise ValueError("Failed to authenticate with Gmail API")
    
    def fetch_emails(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query string
            
        Returns:
            List of structured email objects
        """
        if not self.service:
            print("Gmail service not authenticated")
            return []
            
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("No messages found.")
                return []
                
            print(f"Found {len(messages)} messages.")
            print("-" * 50)
            
            message_list = []
            
            for message in messages:
                email = self.get_email(message['id'])
                if email:
                    message_list.append(email)
            
            return message_list
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email(self, email_id: str) -> Dict[str, Any]:
        """
        Get a specific email by ID.
        
        Args:
            email_id: ID of the email to retrieve
            
        Returns:
            Structured email object
        """
        if not self.service:
            print("Gmail service not authenticated")
            return None
            
        try:
            msg = self.service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            return self.parser.parse_email(msg)
            
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
    
    def update_email(self, message_id: str, **kwargs) -> bool:
        """
        Update an email's properties.
        
        Args:
            message_id: ID of the email to update
            **kwargs: Properties to update (supported: mark_as_read, move_to_label)
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self.service:
            print("Gmail service not authenticated")
            return False
        
        mark_as_read = kwargs.get('mark_as_read', False)
        move_to_label = kwargs.get('move_to_label', None)
            
        if not mark_as_read and not move_to_label:
            print("No update actions specified")
            return False
            
        try:
            modifications = {}
            
            if mark_as_read:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='minimal'
                ).execute()
                
                current_labels = msg.get('labelIds', [])
                
                if 'UNREAD' in current_labels:
                    modifications['removeLabelIds'] = ['UNREAD']
                    print(f"Marking message {message_id} as read")
                else:
                    print(f"Message {message_id} is already marked as read")
            
            if move_to_label:
                add_labels = [move_to_label]
                remove_labels = []
                
                if move_to_label != 'INBOX':
                    if 'removeLabelIds' not in modifications:
                        msg = self.service.users().messages().get(
                            userId='me',
                            id=message_id,
                            format='minimal'
                        ).execute()
                        current_labels = msg.get('labelIds', [])
                    
                    if 'INBOX' in current_labels:
                        remove_labels.append('INBOX')
                
                if add_labels:
                    modifications['addLabelIds'] = add_labels
                
                if remove_labels:
                    if 'removeLabelIds' in modifications:
                        modifications['removeLabelIds'].extend(remove_labels)
                    else:
                        modifications['removeLabelIds'] = remove_labels
            
            if modifications:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body=modifications
                ).execute()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating email: {e}")
            return False


def main():
    """Example usage of the Gmail service."""
    try:
        # Create authenticator
        authenticator = GmailAuthenticator(
            credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
            token_file=os.getenv('GMAIL_TOKEN_FILE')
        )
        
        # Create Gmail service
        gmail_service = GmailService(authenticator)
        
        # Fetch emails
        emails = gmail_service.fetch_emails(max_results=5)
        
        if emails:
            print("\nEmail Summary:")
            for email in emails:
                print(f"Subject: {email['Subject']}")
                print(f"From: {email['From']}")
                print(f"Date: {email['Date Received']}")
                print("-" * 50)
            
            # Mark first email as read
            first_email_id = emails[0]['unique_id']
            if gmail_service.update_email(first_email_id, mark_as_read=True):
                print(f"Marked email '{emails[0]['Subject']}' as read")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()