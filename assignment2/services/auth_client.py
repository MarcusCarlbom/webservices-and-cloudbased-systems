import requests

AUTH_SERVICE_URL = "http://127.0.0.1:8001"

def validate_token(token):
    try:
        r = requests.post(f"{AUTH_SERVICE_URL}/users/validate", json={"token": token})
        if r.status_code == 200:
            return r.json().get("username")
        return None
    except Exception:
        return None