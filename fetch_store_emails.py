from singleton import rule_operations
import os


def main(rule_operations):
    """
    Fetches emails from Gmail and stores them in a SQLite database.
    """
    
    max_results = os.getenv('MAX_EMAILS', 100)
    rule_operations.fetch_and_store_emails(max_results=max_results)


if __name__ == "__main__":
    print("Fetching and storing emails from Gmail...")
    main(rule_operations)
    print("Successfully fetched and stored emails in the database")