"""
Gmail Module for authenticating, fetching, and updating emails in Gmail.
"""
import os
import pickle
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

class Gmail:
    """
    Gmail class for interacting with Gmail API.
    Handles authentication and provides methods for email operations.
    """
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """
        Initialize the Gmail class with credentials.
        
        Args:
            credentials_file: Path to the credentials.json file (from Google Cloud Console)
            token_file: Path to store/retrieve the token.pickle file
        
        Raises:
            ValueError: If authentication fails
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get credentials from .env if not provided
        self.credentials_file = credentials_file or os.getenv('GMAIL_CREDENTIALS_FILE')
        self.token_file = token_file or os.getenv('GMAIL_TOKEN_FILE')
        
        if not self.credentials_file:
            raise ValueError("Credentials file path not provided in arguments or .env file")
        
        # Default token file location if not specified
        if not self.token_file:
            self.token_file = 'token.pickle'
        
        # Authenticate and build the service
        self.service = self._authenticate()
        
        if not self.service:
            raise ValueError("Failed to authenticate with Gmail API")
    
    def _authenticate(self):
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
    
    def fetch_emails(self, max_results: int = 10, query: str = ""):
        if not self.service:
            print("Gmail service not authenticated")
            return None
            
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
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_content = self.get_email_structure(msg)
                
                message_list.append(email_content)
            
            return message_list
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return None

    def get_email_structure(self, content):
        try:
            headers = content['payload']['headers']
            id = content['id']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            body = self._get_message_body(content['payload'])
            
            return {
                'unique_id': id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }

        except Exception as e:
            print(f"Error getting email structure: {e}")
            return None
    
    def _get_message_body(self, payload):
        """
        Extract the message body from the payload.
        """

        # If the message is simple
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
        # If the message is multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    
                if 'parts' in part:
                    body = self._get_message_body(part)
                    if body:
                        return body
                        
        return None
        
    def update_email(self, message_id: str, mark_as_read: bool = False, move_to_label: Optional[str] = None):
        if not self.service:
            print("Gmail service not authenticated")
            return False
            
        if not mark_as_read and not move_to_label:
            raise ValueError("At least one update action must be specified")
            
        try:
            modifications = {}
            
            if mark_as_read:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='minimal'
                ).execute()
                
                current_labels = msg.get('labelIds', [])
                print("current_labels", current_labels)
                
                if 'UNREAD' in current_labels:
                    current_labels.remove('UNREAD')
                    
                    modifications['removeLabelIds'] = ['UNREAD']
                    print(f"Marking message {message_id} as read")
                else:
                    print(f"Message {message_id} is already marked as read")
            
            if move_to_label:
                add_labels = [move_to_label]
                remove_labels = []
                
                if move_to_label != 'INBOX':
                    if not 'removeLabelIds' in modifications:
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
                        
                print(f"Moving message {message_id} to label '{move_to_label}'")
            
            if modifications:
                result = self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body=modifications
                ).execute()
                
                print(f"Successfully updated message {message_id}")
                return True
            else:
                print("No modifications needed")
                return True
                
        except Exception as e:
            print(f"Error updating email: {e}")
            return False

def main():
    try:
        print("Initializing Gmail client...")
        gmail = Gmail()
        
        print("Authentication successful!")
        print(f"Gmail service initialized: {gmail.service is not None}")

        emails = gmail.fetch_emails()
        print(emails)
        # email_id = emails[0]['id']

        # gmail.update_email(email_id, mark_as_read=True)
        # gmail.update_email(email_id, move_to_label='UPDATES')
    
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()