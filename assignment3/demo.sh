#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "--- Start services ---"
docker compose up -d

echo "--- Register (409 if alice already exists is harmless) ---"
REGISTER=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}')
echo "Register HTTP $REGISTER"

echo "--- Login ---"
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"

echo "--- Create URL 1 ---"
ID1=$(curl -s -X POST http://127.0.0.1:8080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.example.com"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created ID: $ID1"

echo "--- Create URL 2 ---"
ID2=$(curl -s -X POST http://127.0.0.1:8080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.wikipedia.org"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created ID: $ID2"

echo "--- List all URLs ---"
curl -s http://127.0.0.1:8080/ \
  -H "Authorization: $TOKEN" | python3 -m json.tool

echo "--- Retrieve $ID1 ---"
curl -s http://127.0.0.1:8080/$ID1 \
  -H "Authorization: $TOKEN" | python3 -m json.tool

echo "--- Delete $ID1 ---"
curl -s -o /dev/null -X DELETE http://127.0.0.1:8080/$ID1 \
  -H "Authorization: $TOKEN" -w "HTTP %{http_code}\n"

echo "--- Confirm $ID1 is gone (expect 404) ---"
curl -s -o /dev/null http://127.0.0.1:8080/$ID1 \
  -H "Authorization: $TOKEN" -w "HTTP %{http_code}\n"

echo "--- List again ($ID1 deleted, $ID2 still present) ---"
curl -s http://127.0.0.1:8080/ \
  -H "Authorization: $TOKEN" | python3 -m json.tool

echo "--- Logout (expect HTTP 403 with no token) ---"
unset TOKEN
curl -s -o /dev/null http://127.0.0.1:8080/ -w "HTTP %{http_code}\n"
echo "Done."
