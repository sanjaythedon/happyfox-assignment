"""
Test script for Gmail module.
"""
from gmail_module import Gmail

def main():
    try:
        # Initialize the Gmail client
        # This will trigger the authentication flow if needed
        print("Initializing Gmail client...")
        gmail = Gmail()
        
        # If we get here, authentication was successful
        print("Authentication successful!")
        print(f"Gmail service initialized: {gmail.service is not None}")
        
        # You can add more test functionality here
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
