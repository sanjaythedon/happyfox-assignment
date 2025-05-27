from RuleOperations.rule_operations import RuleOperations
from Gmail.gmail import GmailService, GmailAuthenticator
from Database.sqlite import SQLiteDatabase
from FileHandler import JSONFileHandler
import os

def main():
    gmail_authenticator = GmailAuthenticator(
        credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
        token_file=os.getenv('GMAIL_TOKEN_FILE')
    )
    gmail = GmailService(gmail_authenticator)
    db = SQLiteDatabase()
    file_handler = JSONFileHandler('rules1.json')
    
    rule_operations = RuleOperations(gmail, db, file_handler)
    # rule_operations.fetch_and_store_emails()
    rule_operations.run_operations()

if __name__ == "__main__":
    main()