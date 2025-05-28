# HappyFox Assignment

A Python application that integrates Gmail access with rule-based email processing and local database storage.

## Modules

### 1. Gmail Module

A Python module for Gmail access to authenticate, fetch, and update emails in Gmail using Google's Gmail API.

#### Features

- OAuth authentication with Gmail API
- Token persistence for future sessions
- Error handling for authentication failures

### 2. SQLite Database Module

A lightweight database module that provides a simple interface for SQLite operations.

#### Features

- Create tables with custom columns and data types
- Insert data into tables
- Read data with optional column selection and conditions
- Update data based on conditions

### 3. Rule Operations Module

A module for defining and applying rules to process emails based on specific conditions.

### 4. File Handler Module

A module for managing file operations, including reading from and writing to files, handling attachments, and processing file-based data.

## Setup

1. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate # On Linux/Mac
   .\venv\Scripts\activate # On Windows
   ```

2. Install the required dependencies:
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
   TEST_GMAIL_CREDENTIALS_FILE=path/to/your/test_credentials.json
   TEST_GMAIL_TOKEN_FILE=path/to/store/test_token.pickle
   TEST_EMAIL_RECIPIENT=your_test_email@example.com
   TEST_EMAIL_SENDER=your_test_email@example.com
   ```

## Running Functions Separately

You can also run specific functions separately using dedicated scripts:

1. **Fetch and Store Emails Only**:

```bash
python fetch_store_emails.py
```

This script will connect to Gmail, fetch emails according to your settings, and store them in the database.

2. **Apply Rules Only** (assumes emails are already in the database):

```bash
python run_operations.py
```

This script will load emails from the database and apply the rules defined in your rules file.


### Customizing the Workflow

You can customize the workflow by modifying these parameters:

- **Number of emails**: Add the `MAX_EMAILS` value in your `.env` file to limit the number of emails fetched from Gmail ( default is 100 )
- **Rules file**: Add the `RULES_FILE` value in your `.env` file to use a different rules file ( default is `rules.json` )
- **Rule definitions**: Edit the `RULES_FILE` file to define different rules
- **Database file**: Add the database filename in `.env` file `DATABASE_FILE` to use a different database ( default is `app.db` )

## Testing

The application includes comprehensive tests to check integration of all modules:

1. Make sure you have credentials available for a test account:
   - Create a separate credentials.json file for testing
   - Add the path to TEST_GMAIL_CREDENTIALS_FILE in .env
   - Specify TEST_EMAIL_SENDER and TEST_EMAIL_RECIPIENT in .env

2. Run integration tests:
   ```
   python test.py
   ```

## Requirements

- Python 3.6+
- Google API Python Client
- Google Auth Library
- Python dotenv
