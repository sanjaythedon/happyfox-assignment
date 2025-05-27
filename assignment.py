from gmail import Gmail
from db import Database
from file_handler import JSONFileHandler
from datetime import datetime, timedelta, timezone


class Assignment:
    """
    A class that integrates Gmail, database, and file handling functionality.
    """
    
    def __init__(self, gmail_obj, db_obj, file_obj):
        self.gmail = gmail_obj
        self.db = db_obj
        self.file_handler = file_obj
        
    def run_operations(self):
        try:
            rules = self.file_handler.read_json()
            print(f"Successfully loaded {len(rules)} rule(s)")
            
            for rule in rules:
                rule_name = rule.get('rule_name', 'Unnamed Rule')
                rule_collection_predicate = rule.get('rule_collection_predicate', 'all')
                rule_conditions = rule.get('rules', [])
                
                # Build SQL query based on rule conditions
                sql_conditions = []
                condition_values = []
                
                for condition in rule_conditions:
                    field_name = condition.get('field_name').title()
                    predicate = condition.get('predicate')
                    value = condition.get('value')
                    unit = condition.get('unit', None)
                    
                    # Skip if any required field is missing
                    if not all([field_name, predicate, value]):
                        continue
                    
                    # Handle different predicates for string values
                    if predicate == 'contains':
                        sql_conditions.append(f"\"{field_name}\" LIKE ?")
                        condition_values.append(f"%{value}%")
                    elif predicate == 'does not contain':
                        sql_conditions.append(f"\"{field_name}\" NOT LIKE ?")
                        condition_values.append(f"%{value}%")
                    elif predicate == 'equals':
                        sql_conditions.append(f"\"{field_name}\" = ?")
                        condition_values.append(value)
                    elif predicate == 'does not equal':
                        sql_conditions.append(f"\"{field_name}\" != ?")
                        condition_values.append(value)
                    # Handle datetime predicates
                    elif predicate in ['is less than', 'is greater than'] and field_name == 'Date Received':
                        # Calculate the date based on value and unit
                        try:
                            value_int = int(value)
                            current_date = datetime.now(timezone.utc)
                            
                            if unit == 'days':
                                if predicate == 'is less than':
                                    # Emails received less than X days ago
                                    target_date = current_date - timedelta(days=value_int)
                                    sql_conditions.append(f"\"{field_name}\" > ?")
                                else:  # is greater than
                                    # Emails received more than X days ago
                                    target_date = current_date - timedelta(days=value_int)
                                    sql_conditions.append(f"\"{field_name}\" < ?")
                                
                                condition_values.append(target_date.strftime('%Y-%m-%d %H:%M:%S'))
                            elif unit == 'months':
                                # Calculate months by approximating 30 days per month
                                if predicate == 'is less than':
                                    target_date = current_date - timedelta(days=30 * value_int)
                                    sql_conditions.append(f"\"{field_name}\" > ?")
                                else:  # is greater than
                                    target_date = current_date - timedelta(days=30 * value_int)
                                    sql_conditions.append(f"\"{field_name}\" < ?")
                                    
                                condition_values.append(target_date.strftime('%Y-%m-%d %H:%M:%S'))
                        except (ValueError, TypeError) as e:
                            print(f"Error processing datetime condition: {e}")
                            continue
                
                # Combine conditions based on rule_collection_predicate
                if sql_conditions:
                    if rule_collection_predicate.lower() == 'all':
                        condition_str = " AND ".join(sql_conditions)
                    else:  # 'any'
                        condition_str = " OR ".join(sql_conditions)
                    
                    print(f"Rule '{rule_name}' SQL condition: {condition_str}")
                    print(f"Condition values: {condition_values}")
                    
                    # Query the database with these conditions
                    matching_emails = self.db.read("emails", condition=condition_str, condition_values=condition_values)
                    print(f"Found {len(matching_emails)} emails matching rule '{rule_name}'")
                    
                    # Process operations from rule['operations']
                    operations = rule.get('operations', [])
                    if operations and matching_emails:
                        print(f"Applying {len(operations)} operations to {len(matching_emails)} emails")
                        
                        for email in matching_emails:
                            email_id = email.get('unique_id')
                            if not email_id:
                                print(f"Warning: Email missing unique ID, skipping operations")
                                continue
                                
                            print(f"Processing operations for email: {email.get('Subject', 'No Subject')}")
                            
                            # Initialize operation variables
                            mark_as_read = None
                            move_to_label = None
                            
                            # Process each operation
                            for operation in operations:
                                action = operation.get('action')
                                
                                if action == 'Mark as Read':
                                    mark_as_read = True
                                    print(f"  - Will mark as read")
                                    
                                elif action == 'Move message':
                                    destination = operation.get('destination').upper()
                                    if destination:
                                        move_to_label = destination
                                        print(f"  - Will move to: {destination}")
                            
                            # Apply the operations using Gmail API
                            if mark_as_read is not None or move_to_label is not None:
                                try:
                                    result = self.gmail.update_email(
                                        message_id=email_id,
                                        mark_as_read=mark_as_read if mark_as_read is not None else False,
                                        move_to_label=move_to_label
                                    )
                                    
                                    if result:
                                        print(f"Successfully applied operations to email: {email.get('Subject', 'No Subject')}")
                                    else:
                                        print(f"Failed to apply operations to email: {email.get('Subject', 'No Subject')}")
                                except Exception as e:
                                    print(f"Error applying operations to email: {e}")
                    else:
                        print(f"No operations to apply or no matching emails for rule '{rule_name}'")
                    
            
            return rules
        except Exception as e:
            print(f"Error reading rules file: {e}")
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
    gmail = Gmail()
    db = Database()
    file_handler = JSONFileHandler('rules1.json')
    
    assignment = Assignment(gmail, db, file_handler)
    # assignment.fetch_and_store_emails()
    assignment.run_operations()