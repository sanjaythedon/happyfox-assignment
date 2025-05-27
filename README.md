# Gmail Module

A Python module for Gmail access to authenticate, fetch, and update emails in Gmail using Google's Gmail API.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file

3. Create a `.env` file based on the `.env.example` template:
   ```
   GMAIL_CREDENTIALS_FILE=path/to/your/credentials.json
   GMAIL_TOKEN_FILE=path/to/store/token.pickle
   ```

## Usage

```python
from gmail_module import Gmail

# Initialize the Gmail client
gmail = Gmail()
# OR specify paths directly
# gmail = Gmail(credentials_file='path/to/credentials.json', token_file='path/to/token.pickle')

# The first time you run this, it will open a browser window for authentication
# After authenticating, the token will be saved for future use
```

## Features

- OAuth authentication with Gmail API
- Token persistence for future sessions
- Error handling for authentication failures

## Requirements

- Python 3.6+
- Google API Python Client
- Google Auth Library
- Python dotenv
