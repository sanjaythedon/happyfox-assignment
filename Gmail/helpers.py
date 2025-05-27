import base64
from typing import Dict, Any


class EmailParser:
    """
    Handles parsing of email content.
    """

    @staticmethod
    def decode_text(text):
        """
        Decodes a base64 encoded text.
        
        Args:
            text: Base64 encoded text
            
        Returns:
            Decoded text
        """
        return base64.urlsafe_b64decode(text).decode('utf-8')   

    @staticmethod
    def get_message_body(payload):
        """
        Extract the message body from the payload.
        
        Args:
            payload: Email payload from Gmail API
            
        Returns:
            Message body as a string, or None if not found
        """

        # If the message is simple
        if 'body' in payload and payload['body'].get('data'):
            return EmailParser.decode_text(payload['body']['data'])
            
        # If the message is multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    return EmailParser.decode_text(part['body']['data'])
                        
                if 'parts' in part:
                    body = EmailParser.get_message_body(part)
                    if body:
                        return body
                            
        return None

    @staticmethod
    def parse_email(content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse email content into a structured format.
        
        Args:
            content: Raw email content from Gmail API
            
        Returns:
            Structured email data
        """
        try:
            headers = content['payload']['headers']
            email_id = content['id']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            body = EmailParser.get_message_body(content['payload'])
            
            return {
                'unique_id': email_id,
                'Subject': subject,
                'From': sender,
                'Date Received': date,
                'Message': body
            }
        except Exception as e:
            print(f"Error parsing email: {e}")
            return None