from RuleOperations.rule_operations import RuleOperations
from Gmail.gmail import GmailService, GmailAuthenticator
from Database.sqlite import SQLiteDatabase, SQLiteConnection, SQLiteTableManager, SQLiteDataManager
from FileHandler import JSONFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

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