import requests
import json

# Make sure these are running:
# Terminal 1: cd auth_service && python3 auth_rest_service.py  (port 8001)
# Terminal 2: python3 rest_service.py                          (port 8000)
# Terminal 3: mongod --port 27420 --dbpath /your/db/path

auth_url = "http://127.0.0.1:8001"
base_url = "http://127.0.0.1:8000"

# Register - expect 201
r = requests.post(f"{auth_url}/users", json={"username": "test", "password": "test"})
print(f"Register: {r.status_code}")

# Login - expect 200
r = requests.post(f"{auth_url}/users/login", json={"username": "test", "password": "test"})
print(f"Login: {r.status_code}")
token = r.json().get("token")

# Wrong password - expect 403
r = requests.post(f"{auth_url}/users/login", json={"username": "test", "password": "wrong"})
print(f"Bad login: {r.status_code}")

headers = {"Authorization": token}
bad_headers = {"Authorization": "wrong"}

# Post without auth - expect 403
r = requests.post(base_url, headers=bad_headers, json={"value": "https://google.com"})
print(f"Post no auth: {r.status_code}")

# Post with auth - expect 201
r = requests.post(base_url, headers=headers, json={"value": "https://google.com"})
print(f"Post: {r.status_code}")
url_id = r.json().get("id")

# Get by id - expect 301
r = requests.get(f"{base_url}/{url_id}", headers=headers, allow_redirects=False)
print(f"Get id: {r.status_code}")

# Get all - expect 200
r = requests.get(base_url, headers=headers)
print(f"Get all: {r.status_code}")

# Put - expect 200
r = requests.put(f"{base_url}/{url_id}", headers=headers, json={"value": "https://github.com"})
print(f"Put: {r.status_code}")

# Delete - expect 204
r = requests.delete(f"{base_url}/{url_id}", headers=headers)
print(f"Delete: {r.status_code}")

# Delete all - expect 404
r = requests.delete(base_url, headers=headers)
print(f"Delete root: {r.status_code}")