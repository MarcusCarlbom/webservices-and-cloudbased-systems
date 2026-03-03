# Demo – URL Shortener Service

End-to-end walkthrough: register → login → create URL → list → delete → logout.
All commands go through the **nginx reverse proxy on port 8080**, which routes
`/users*` to the auth service and everything else to the URL shortener.
All commands are copy-paste ready for a bash terminal.

Services must be running before starting:
```bash
cd assignment3/
docker compose up -d
```

Create a user

```bash
curl -s -X POST http://127.0.0.1:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -m json.tool
```

```json
{
    "message": "User created successfully"
}
```

Login and capture the token

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"
```

Expected HTTP 200
```
Token: eyJhbGciOiAiSFMyNTYi...
```

The token is valid for 1 hour. All subsequent requests use `$TOKEN` as the `Authorization` header

---

Create a shortened URL

```bash
curl -s -X POST http://127.0.0.1:8080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.example.com"}' | python3 -m json.tool
```

Expected HTTP 201
```json
{
    "id": "1"
}
```

Create a second URL
```bash
curl -s -X POST http://127.0.0.1:8080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.wikipedia.org"}' | python3 -m json.tool
```

Expected HTTP 201
```json
{
    "id": "2"
}
```

List all shortened URLs

```bash
curl -s http://127.0.0.1:8080/ \
  -H "Authorization: $TOKEN" | python3 -m json.tool
```

Expected HTTP 200
```json
{
    "urls": [
        "1",
        "2"
    ]
}
```

Retrieve a specific URL

```bash
curl -s http://127.0.0.1:8080/1 \
  -H "Authorization: $TOKEN" | python3 -m json.tool
```

Expected HTTP 301
```json
{
    "value": "https://www.example.com"
}
```

Delete a URL
```bash
curl -s -X DELETE http://127.0.0.1:8080/1 \
  -H "Authorization: $TOKEN" -w "%{http_code}\n"
```

Expected HTTP 204 (empty body, status code printed by `-w`):
```
204
```

Confirm it is gone
```bash
curl -s http://127.0.0.1:8080/1 \
  -H "Authorization: $TOKEN" -w "%{http_code}\n"
```

Expected HTTP 404
```
404
```

List again to confirm only URL 2 remains
```bash
curl -s http://127.0.0.1:8080/ \
  -H "Authorization: $TOKEN" | python3 -m json.tool
```

Expected
```json
{
    "urls": [
        "2"
    ]
}
```
Logout
JWT is stateless so the server holds no session. Logout is simply discarding the token from the client side:

```bash
unset TOKEN
echo "Logged out. Token: '${TOKEN}'"
```

Expected
```
Logged out. Token: ''
```

Any request made after unsetting `$TOKEN` will be rejected with 403
```bash
curl -s http://127.0.0.1:8080/ -w "%{http_code}\n"
```

Expected
```
403
```