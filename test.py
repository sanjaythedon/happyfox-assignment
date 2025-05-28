import unittest
import os
from dotenv import load_dotenv
from Gmail.gmail import GmailService, GmailAuthenticator
from Database.sqlite import SQLiteDatabase
from FileHandler.json import JSONFileHandler
from RuleOperations.rule_operations import RuleOperations

class TestEmailRuleOperations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        
        cls.gmail_authenticator = GmailAuthenticator(
            credentials_file=os.getenv('TEST_GMAIL_CREDENTIALS_FILE'),
            token_file=os.getenv('TEST_GMAIL_TOKEN_FILE')
        )
        cls.gmail = GmailService(cls.gmail_authenticator)
        cls.db = SQLiteDatabase(db_path="test_emails.db")
        cls.file_handler = JSONFileHandler('test_rules.json')
        cls.rule_operations = RuleOperations(cls.gmail, cls.db, cls.file_handler)
    
    def setUp(self):
        self.db.execute_query("DROP TABLE IF EXISTS emails")
    
    def test_fetch_and_store_emails(self):
        """Test fetching emails from Gmail and storing them in the database"""
        result = self.rule_operations.fetch_and_store_emails()
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
        
        self.rule_operations.fetch_and_store_emails()
        rules = self.rule_operations.run_operations()
        
        self.assertEqual(len(rules), 1)
    
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
        
        self.rule_operations.fetch_and_store_emails()
        rules = self.rule_operations.run_operations()
        
        self.assertEqual(len(rules), 1)
    
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
                    }
                ],
                "operations": [
                    {
                        "action": "Mark as Read"
                    }
                ]
            },
            {
                "rule_name": "Rule 2",
                "rule_collection_predicate": "any",
                "rules": [
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
        
        self.rule_operations.fetch_and_store_emails()
        rules = self.rule_operations.run_operations()
        
        self.assertEqual(len(rules), 2)
    
    def tearDown(self):
        pass
    
    @classmethod
    def tearDownClass(cls):
        if os.path.exists("test_emails.db"):
            os.remove("test_emails.db")
        if os.path.exists("test_rules.json"):
            os.remove("test_rules.json")

if __name__ == "__main__":
    unittest.main()