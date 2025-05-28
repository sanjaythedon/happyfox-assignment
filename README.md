# HappyFox Assignment

A Python application that integrates Gmail access with rule-based email processing and local database storage.

## Modules

### 1. Gmail Module

A Python module for Gmail access to authenticate, fetch, and update emails in Gmail using Google's Gmail API.

#### Features

- OAuth authentication with Gmail API
- Token persistence for future sessions
- Error handling for authentication failures

#### Usage

```python
from Gmail.gmail import Gmail

# Initialize the Gmail client
gmail = Gmail()
# OR specify paths directly
# gmail = Gmail(credentials_file='path/to/credentials.json', token_file='path/to/token.pickle')

# The first time you run this, it will open a browser window for authentication
# After authenticating, the token will be saved for future use
```

### 2. SQLite Database Module

A lightweight database module that provides a simple interface for SQLite operations.

#### Features

- Create tables with custom columns and data types
- Insert data into tables
- Read data with optional column selection and conditions
- Update data based on conditions

#### Usage

```python
from Database.sqlite import Database

# Initialize the database
db = Database("my_database.db")

# Create a table
db.create_table("emails", {
    "id": "INTEGER PRIMARY KEY",
    "subject": "TEXT",
    "sender": "TEXT",
    "date": "TEXT"
})

# Insert data
db.insert("emails", {"subject": "Hello", "sender": "user@example.com", "date": "2025-05-28"})

# Read data
results = db.read("emails", columns=["subject", "sender"], conditions={"date": "2025-05-28"})
```

### 3. Rule Operations Module

A module for defining and applying rules to process emails based on specific conditions.

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

## Running the Application

The application can be run in different ways depending on your needs:

### Running the Complete Workflow

To run the entire workflow (fetch emails and apply rules):

```bash
python main.py
```

This will execute both the `fetch_and_store_emails` and `run_operations` functions in sequence.

### Running Functions Separately

You can modify main.py to run specific functions separately:

1. **Fetch and Store Emails Only**:

```python
# In main.py
if __name__ == "__main__":
    # Initialize components
    gmail_authenticator = GmailAuthenticator(
        credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
        token_file=os.getenv('GMAIL_TOKEN_FILE')
    )
    gmail = GmailService(gmail_authenticator)
    
    connection_manager = SQLiteConnection(os.getenv('DATABASE_FILE', 'app.db'))
    db = SQLiteDatabase(
        connection_manager=connection_manager,
        table_manager=SQLiteTableManager(connection_manager),
        data_manager=SQLiteDataManager(connection_manager)
    )
    file_handler = JSONFileHandler(os.getenv('RULES_FILE', 'rules.json'))
    
    rule_operations = RuleOperations(gmail, db, file_handler)
    
    # Only fetch and store emails
    print("Fetching and storing emails from Gmail...")
    max_results = os.getenv('MAX_EMAILS', 100)
    rule_operations.fetch_and_store_emails(max_results=max_results)
    print("Successfully fetched and stored emails in the database")
```

2. **Apply Rules Only** (assumes emails are already in the database):

```python
# In main.py
if __name__ == "__main__":
    # Initialize components
    gmail_authenticator = GmailAuthenticator(
        credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
        token_file=os.getenv('GMAIL_TOKEN_FILE')
    )
    gmail = GmailService(gmail_authenticator)
    
    connection_manager = SQLiteConnection(os.getenv('DATABASE_FILE', 'app.db'))
    db = SQLiteDatabase(
        connection_manager=connection_manager,
        table_manager=SQLiteTableManager(connection_manager),
        data_manager=SQLiteDataManager(connection_manager)
    )
    rules_file = os.getenv('RULES_FILE', 'rules.json')
    file_handler = JSONFileHandler(rules_file)
    
    rule_operations = RuleOperations(gmail, db, file_handler)
    
    # Only apply rules to existing emails
    print("Applying rules to emails...")
    rules = rule_operations.run_operations()
    print(f"Successfully applied {len(rules)} rule(s) to matching emails")
```

### Customizing the Workflow

You can customize the workflow by modifying these parameters:

- **Number of emails**: Change the `MAX_EMAILS` value in your `.env` file
- **Rules file**: Change the `RULES_FILE` value in your `.env` file to use a different rules file
- **Rule definitions**: Edit the `RULES_FILE` file to define different rules
- **Database file**: Change the database filename in `.env` file `DATABASE_FILE` to use a different database

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
