import unittest
import os
from dotenv import load_dotenv
from Gmail.gmail import GmailService, GmailAuthenticator
from Database.sqlite import SQLiteDatabase, SQLiteConnection, SQLiteTableManager, SQLiteDataManager
from FileHandler.json import JSONFileHandler
from RuleOperations.rule_operations import RuleOperations

class TestEmailRuleOperations(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        
        self.gmail_authenticator = GmailAuthenticator(
            credentials_file=os.getenv('TEST_GMAIL_CREDENTIALS_FILE'),
            token_file=os.getenv('TEST_GMAIL_TOKEN_FILE')
        )
        self.gmail = GmailService(self.gmail_authenticator)

        self.max_results = 10
        db_path = 'test_emails.db'
        connection_manager = SQLiteConnection(db_path)
        table_manager = SQLiteTableManager(connection_manager)
        data_manager = SQLiteDataManager(connection_manager)
        self.db = SQLiteDatabase(
            connection_manager=connection_manager,
            table_manager=table_manager,
            data_manager=data_manager
        )

        self.file_handler = JSONFileHandler('test_rules.json')
        self.rule_operations = RuleOperations(self.gmail, self.db, self.file_handler)
    
    def test_fetch_and_store_emails(self):
        """Test fetching emails from Gmail and storing them in the database"""
        result = self.rule_operations.fetch_and_store_emails(self.max_results)
        self.assertTrue(result)
        
        emails = self.db.read("emails")
        self.assertGreater(len(emails), 0)
    
    def test_rule_with_contains_condition(self):
        """Test rule with 'contains' condition"""
        test_rule = {
            "rule_name": "Test Contains Rule",
            "rule_collection_predicate": "all",
            "rules": [
                {
                    "field_name": "Subject",
                    "predicate": "contains",
                    "value": "Test"
                }
            ],
            "operations": [
                {
                    "action": "Mark as Read"
                }
            ]
        }
        self.file_handler.write([test_rule])
        
        self.rule_operations.fetch_and_store_emails(self.max_results)
        success_count = self.rule_operations.run_operations()
        
        self.assertGreater(success_count, 0)
    
    def test_rule_with_date_condition(self):
        """Test rule with date condition"""
        test_rule = {
            "rule_name": "Test Date Rule",
            "rule_collection_predicate": "all",
            "rules": [
                {
                    "field_name": "Date Received",
                    "predicate": "is less than",
                    "value": "7",
                    "unit": "days"
                }
            ],
            "operations": [
                {
                    "action": "Move message",
                    "destination": "INBOX"
                }
            ]
        }
        self.file_handler.write([test_rule])
        
        self.rule_operations.fetch_and_store_emails(self.max_results)
        success_count = self.rule_operations.run_operations()
        
        self.assertEqual(success_count, 10)
    
    def test_multiple_rules(self):
        """Test processing multiple rules"""
        test_rules = [
            {
                "rule_name": "Rule 1",
                "rule_collection_predicate": "all",
                "rules": [
                    {
                        "field_name": "From",
                        "predicate": "contains",
                        "value": "test"
                    },
                    {
                        "field_name": "Subject",
                        "predicate": "contains",
                        "value": "important"
                    }
                ],
                "operations": [
                    {
                        "action": "Move message",
                        "destination": "IMPORTANT"
                    }
                ]
            }
        ]
        self.file_handler.write(test_rules)
        
        self.rule_operations.fetch_and_store_emails(self.max_results)
        success_count = self.rule_operations.run_operations()
        
        self.assertEqual(success_count, 2)
    
    def tearDown(self):
        if os.path.exists("test_emails.db"):
            os.remove("test_emails.db")
        if os.path.exists("test_rules.json"):
            os.remove("test_rules.json")
        

if __name__ == "__main__":
    unittest.main()