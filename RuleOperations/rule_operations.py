from datetime import datetime

from RuleOperations.helpers import RuleParser, EmailOperationsBundler


class RuleOperations:
    """
    Class for managing email rule operations.
    This class handles loading rules from a file, fetching emails from Gmail,
    storing them in a database, and applying operations based on defined rules.
    
    Attributes:
        gmail (GmailService): Gmail service object
        db (SQLiteDatabase): Database object
        file_handler (JSONFileHandler): File handler object
    """
    
    def __init__(self, gmail_obj, db_obj, file_obj):
        self.gmail = gmail_obj
        self.db = db_obj
        self.file_handler = file_obj
        
    def run_operations(self):
        """
        Runs the operations defined in the rules file.
        
        Returns:
            List of rules that were successfully run
        """
        try:
            print("Loading rules from file...")
            rules = self.file_handler.read()
            print(f"Successfully loaded {len(rules)} rule(s)")
            
            success_count = 0
            for rule in rules:
                rule_name = rule.get('rule_name', 'Unnamed Rule')
                print(f"\nProcessing rule: '{rule_name}'")
                
                print("Parsing rule conditions to SQL...")
                condition_str, condition_values = RuleParser.create_sql_query(rule)
                
                if condition_str:
                    print(f"Rule '{rule_name}' SQL condition: {condition_str}")
                    print(f"Condition values: {condition_values}")
                    
                    print("Querying database for matching emails...")
                    matching_emails = self.db.read("emails", condition=condition_str, condition_values=condition_values)
                    print(f"Found {len(matching_emails)} emails matching rule '{rule_name}'")
                    
                    operations = rule.get('operations', [])

                    if operations and matching_emails:
                        print(f"Applying {len(operations)} operations to {len(matching_emails)} emails")
                        
                        print("Bundling email operations...")
                        email_operations = EmailOperationsBundler.bundle_email_operations(operations)
                        
                        rule_success_count = 0
                        for i, email in enumerate(matching_emails):
                            email_id = email.get('unique_id')
                            if not email_id:
                                print(f"Warning: Email missing unique ID, skipping operations")
                                continue
                                
                            print(f"Processing operations for email {i+1}/{len(matching_emails)}: {email.get('Subject', 'No Subject')}")
                            
                            is_success = False
                            for j, operation in enumerate(email_operations):
                                print(f"Applying operation {j+1}/{len(email_operations)}...")
                                result = operation.apply(email_id, self.gmail)
                                if result:
                                    is_success = True
                                    print("Operation succeeded")
                                else:
                                    print("Operation failed")

                            rule_success_count += 1 if is_success else 0
                            
                        print(f"Successfully applied operations to {rule_success_count} emails for '{rule_name}'")
                        success_count += rule_success_count
                    else:
                        print(f"No operations to apply or no matching emails for rule '{rule_name}'")
                else:
                    print(f"Warning: Could not create SQL condition for rule '{rule_name}'")
            
            print("\nRule processing completed successfully")
            return success_count
        except Exception as e:
            print(f"Error in run_operations: {e}")
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return None

    def fetch_and_store_emails(self, max_results: int = 100):
        """
        Fetches emails using the Gmail module and stores them in the database.

        Args:
            max_results: Maximum number of emails to fetch from gmail and store in database
            
        Returns:
            True if emails were successfully fetched and stored, False otherwise
        """
        try:
            print("Creating emails table if it doesn't exist...")
            columns = {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "unique_id": "TEXT UNIQUE",
                "Subject": "TEXT",
                "\"From\"": "TEXT",
                "\"Date Received\"": "DATETIME",
                "Message": "TEXT"
            }
            
            self.db.create_table("emails", columns)
            
            print(f"Fetching up to {max_results} emails from Gmail...")
            emails = self.gmail.fetch_emails(max_results=max_results)
            if not emails:
                print("No emails fetched from Gmail")
                return False
                
            print(f"Processing {len(emails)} emails for storage...")
            for i, email in enumerate(emails):
                try:
                    print(f"Processing email {i+1}/{len(emails)}: {email.get('Subject', 'No Subject')}")
                    date_str = email['Date Received'].split('(')[0].strip()
                    parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print(f"Could not parse date format: {email['Date Received']}")
                    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                email_data = {
                    "unique_id": email['unique_id'],
                    "Subject": email['Subject'],
                    "\"From\"": email['From'],
                    "\"Date Received\"": formatted_date,
                    "Message": email['Message'] if email['Message'] else ""
                }
                
                self.db.insert("emails", email_data)
                print(f"Successfully stored email: {email['Subject'][:50]}{'...' if len(email['Subject']) > 50 else ''}")
            
            print(f"Email fetch and store operation completed successfully. {len(emails)} emails stored.")
            return True
            
        except Exception as e:
            print(f"Error in fetch_and_store_emails: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            return False