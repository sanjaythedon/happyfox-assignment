import os
from Gmail import GmailService, GmailAuthenticator
from Database import SQLiteDatabase
from FileHandler import JSONFileHandler
from datetime import datetime


from RuleOperations.helpers import RuleParser, EmailOperationsBundler


class RuleOperations:
    """
    A class that integrates Gmail, database, and file handling functionality.
    """
    
    def __init__(self, gmail_obj, db_obj, file_obj):
        self.gmail = gmail_obj
        self.db = db_obj
        self.file_handler = file_obj
        
    def run_operations(self):
        try:
            # Load rules from the file handler
            rules = self.file_handler.read()
            print(f"Successfully loaded {len(rules)} rule(s)")
            
            for rule in rules:
                rule_name = rule.get('rule_name', 'Unnamed Rule')
                
                # Use RuleParser to create SQL query from rule conditions
                condition_str, condition_values = RuleParser.create_sql_query(rule)
                
                if condition_str:
                    print(f"Rule '{rule_name}' SQL condition: {condition_str}")
                    print(f"Condition values: {condition_values}")
                    
                    # Query the database with these conditions
                    matching_emails = self.db.read("emails", condition=condition_str, condition_values=condition_values)
                    print(f"Found {len(matching_emails)} emails matching rule '{rule_name}'")
                    
                    # Process operations from rule['operations']
                    operations = rule.get('operations', [])
                    if operations and matching_emails:
                        print(f"Applying {len(operations)} operations to {len(matching_emails)} emails")
                        
                        # Create email operations based on rule operations
                        email_operations = EmailOperationsBundler.bundle_email_operations(operations)
                        
                        # Apply operations to each matching email
                        for email in matching_emails:
                            email_id = email.get('unique_id')
                            if not email_id:
                                print(f"Warning: Email missing unique ID, skipping operations")
                                continue
                                
                            print(f"Processing operations for email: {email.get('Subject', 'No Subject')}")
                            
                            # Apply each operation to the email
                            for operation in email_operations:
                                operation.apply(email_id, self.gmail)
                    else:
                        print(f"No operations to apply or no matching emails for rule '{rule_name}'")
            
            return rules
        except Exception as e:
            print(f"Error in run_operations: {e}")
            return None

    def fetch_and_store_emails(self):
        """
        Fetches emails using the Gmail module and stores them in the database.
        """
        try:
            columns = {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "unique_id": "TEXT UNIQUE",
                "Subject": "TEXT",
                "\"From\"": "TEXT",
                "\"Date Received\"": "DATETIME",
                "Message": "TEXT"
            }
            
            self.db.create_table("emails", columns)
            
            emails = self.gmail.fetch_emails(max_results=100)
            if not emails:
                print("No emails fetched")
                return False
                
            for email in emails:
                try:
                    print(email)
                    date_str = email['Date Received'].split('(')[0].strip()
                    parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print(f"Could not parse date: {email['Date Received']}")
                    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                email_data = {
                    "unique_id": email['unique_id'],
                    "Subject": email['Subject'],
                    "\"From\"": email['From'],
                    "\"Date Received\"": formatted_date,
                    "Message": email['Message'] if email['Message'] else ""
                }
                
                self.db.insert("emails", email_data)
                print(f"Stored email: {email['Subject']}")
            
            return True
            
        except Exception as e:
            print(f"Error in fetch_and_store_emails: {e}")
            return False
    
        
if __name__ == "__main__":
    gmail_authenticator = GmailAuthenticator(
        credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
        token_file=os.getenv('GMAIL_TOKEN_FILE')
    )
    gmail = GmailService(gmail_authenticator)
    db = SQLiteDatabase()
    file_handler = JSONFileHandler('rules1.json')
    
    rule_operations = RuleOperations(gmail, db, file_handler)
    # assignment.fetch_and_store_emails()
    rule_operations.run_operations()