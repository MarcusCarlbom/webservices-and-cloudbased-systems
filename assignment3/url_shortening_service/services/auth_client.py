import os
import requests

# Configurable via environment variable so the same image works both locally
# (pointing to localhost) and inside Docker/Kubernetes (pointing to the
# auth-service container by its DNS name).
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://127.0.0.1:8101")

def validate_token(token):
    try:
        r = requests.post(f"{AUTH_SERVICE_URL}/users/validate", json={"token": token})
        if r.status_code == 200:
            return r.json().get("username")
        return None
    except Exception:
        return None
