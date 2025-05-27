from gmail import Gmail
from db import Database
from file_handler import JSONFileHandler
from datetime import datetime


class Assignment:
    """
    A class that integrates Gmail, database, and file handling functionality.
    """
    
    def __init__(self, gmail_obj, db_obj, file_obj):
        self.gmail = gmail_obj
        self.db = db_obj
        self.file_handler = file_obj

    def fetch_and_store_emails(self):
        """
        Fetches emails using the Gmail module and stores them in the database.
        """
        try:
            columns = {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "unique_id": "TEXT UNIQUE",
                "subject": "TEXT",
                "sender": "TEXT",
                "date_time": "DATETIME",
                "body": "TEXT"
            }
            
            self.db.create_table("emails", columns)
            
            emails = self.gmail.fetch_emails()
            if not emails:
                print("No emails fetched")
                return False
                
            for email in emails:
                try:
                    date_str = email['date'].split('(')[0].strip()
                    parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print(f"Could not parse date: {email['date']}")
                    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                email_data = {
                    "unique_id": email['unique_id'],
                    "subject": email['subject'],
                    "sender": email['sender'],
                    "date_time": formatted_date,
                    "body": email['body'] if email['body'] else ""
                }
                
                self.db.insert("emails", email_data)
                print(f"Stored email: {email['subject']}")
            
            return True
            
        except Exception as e:
            print(f"Error in fetch_and_store_emails: {e}")
            return False
    
        
if __name__ == "__main__":
    gmail = Gmail()
    db = Database()
    file_handler = JSONFileHandler('rules.json')
    
    assignment = Assignment(gmail, db, file_handler)
    assignment.fetch_and_store_emails()