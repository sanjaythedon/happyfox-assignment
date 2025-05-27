import json
import os

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


if __name__ == "__main__":
    try:
        handler = JSONFileHandler("test_data.json")
        
        data = handler.read_json()
        
        print("\nSuccessfully read JSON data:")
        print(f"Name: {data['name']}")
        print(f"Age: {data['age']}")
        print(f"Email: {data['email']}")
        print(f"City: {data['address']['city']}")
        print(f"Phone numbers: {', '.join(data['phone_numbers'])}")
        
    except Exception as e:
        print(f"Error: {e}")
