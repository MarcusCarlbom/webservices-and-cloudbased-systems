import json
import base64
import hmac
import hashlib
import time

SECRET_KEY = "super_safe_no_leakage_key_67"

def create_token(username: str) -> str: 
    # create a JWT token with the username and an expiration time of 1 hour
    current_time = int(time.time())
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps({
        "username": username,
        "exp": current_time+3600
    })
    
    encoded_header = base64.urlsafe_b64encode(header.encode()).rstrip(b'=').decode()
    encoded_payload = base64.urlsafe_b64encode(payload.encode()).rstrip(b'=').decode()
    
    signature = hmac.new(SECRET_KEY.encode(), f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def verify_token(token: str) -> str:
    # verify the token and return the username if valid, otherwise return False
    current_time = int(time.time())
    try:
        header, payload, signature = token.split('.')
        test = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        test_encoded = base64.urlsafe_b64encode(test).rstrip(b'=').decode()
        if not hmac.compare_digest(test_encoded, signature):
            return None
        decoded_payload = json.loads(base64.urlsafe_b64decode(payload + '==').decode())
        if decoded_payload.get("exp", 0) < current_time:
            return None
        return decoded_payload.get("username")
    except Exception as e:
        return None