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
        """
        Fetch emails from Gmail and print their details.
        
        Args:
            max_results: Maximum number of emails to fetch (default: 10)
            query: Search query to filter emails (uses Gmail search syntax)
                   Examples: "from:example@gmail.com", "subject:hello", "is:unread"
        
        Returns:
            List of message objects or None if fetching fails
        """
        if not self.service:
            print("Gmail service not authenticated")
            return None
            
        try:
            # Get list of messages
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
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
                
                # Extract body
                body = self._get_message_body(msg['payload'])
                
                # Print email details
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                print(f"Date: {date}")
                print(f"Snippet: {msg['snippet']}")
                
                if body:
                    print(f"Body: {body[:100]}..." if len(body) > 100 else f"Body: {body}")
                else:
                    print("Body: [No readable content]")
                    
                print("-" * 50)
                
                message_list.append(msg)
            
            return message_list
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return None
    
    def _get_message_body(self, payload):
        """
        Extract the message body from the payload.
        
        Args:
            payload: The message payload from Gmail API
            
        Returns:
            Decoded message body as string or None if not found
        """
        # If the message is simple
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
        # If the message is multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    
                # Recursively check parts
                if 'parts' in part:
                    body = self._get_message_body(part)
                    if body:
                        return body
                        
        return None

def main():
    try:
        # Initialize the Gmail client
        # This will trigger the authentication flow if needed
        print("Initializing Gmail client...")
        gmail = Gmail()
        
        # If we get here, authentication was successful
        print("Authentication successful!")
        print(f"Gmail service initialized: {gmail.service is not None}")

        gmail.fetch_emails()
        
        # You can add more test functionality here
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()