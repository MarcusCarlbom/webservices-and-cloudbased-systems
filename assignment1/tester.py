import requests

# Post google as first link
requests.post('http://127.0.0.1:5000/', json={"url": "https://google.com"})

# Test to get the first link, should be a redirection to google
r = requests.get('http://127.0.0.1:5000/1', allow_redirects=False)
print(r.headers.get('Location'))