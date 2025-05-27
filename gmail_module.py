"""
Gmail Module for authenticating, fetching, and updating emails in Gmail.
"""
import os
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any

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