class Assignment:
    """
    A class that integrates Gmail, database, and file handling functionality.
    """
    
    def __init__(self, gmail_obj, db_obj, file_obj):
        """
        Initialize the Assignment with Gmail, database, and file handling objects.
        """
        self.gmail = gmail_obj
        self.db = db_obj
        self.file_handler = file_obj
        
