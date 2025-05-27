from RuleOperations.rule_operations import RuleOperations
from Gmail.gmail import GmailService, GmailAuthenticator
from Database.sqlite import SQLiteDatabase, SQLiteConnection, SQLiteTableManager, SQLiteDataManager
from FileHandler import JSONFileHandler
import os


def main():
    """
    Fetches emails from Gmail and stores them in a SQLite database.
    Then applies rules to the emails.
    """
    
    gmail_authenticator = GmailAuthenticator(
        credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
        token_file=os.getenv('GMAIL_TOKEN_FILE')
    )
    gmail = GmailService(gmail_authenticator)
    
    connection_manager = SQLiteConnection("app.db")
    db = SQLiteDatabase(
        connection_manager=connection_manager,
        table_manager=SQLiteTableManager(connection_manager),
        data_manager=SQLiteDataManager(connection_manager)
    )
    file_handler = JSONFileHandler('rules1.json')
    
    rule_operations = RuleOperations(gmail, db, file_handler)
    rule_operations.fetch_and_store_emails(max_results=100)
    rule_operations.run_operations()

if __name__ == "__main__":
    main()