import base64

def decode_text(text):
    return base64.urlsafe_b64decode(text).decode('utf-8')

def get_message_body(payload):
    """
    Extract the message body from the payload.
    """

    # If the message is simple
    if 'body' in payload and payload['body'].get('data'):
        return decode_text(payload['body']['data'])
            
    # If the message is multipart
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                return decode_text(part['body']['data'])
                    
            if 'parts' in part:
                body = get_message_body(part)
                if body:
                    return body
                        
    return None