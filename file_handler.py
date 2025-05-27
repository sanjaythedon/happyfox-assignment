import json

class JSONFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def read_json(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Invalid JSON format in file: {self.file_path}", '', 0)

