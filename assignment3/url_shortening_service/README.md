# Assignment 3

Prerequisites
- Docker installed
- nginx installed

Build the images
```bash
docker compose build
```

Docker builds `url_shortener` and `auth_service` images locally. Because
`requirements.txt` is copied before the application code, the pip layer is
cached and subsequent rebuilds (when only Python files change) complete in
seconds rather than minutes.

Start all services
```bash
docker compose up -d
```

Verify all four containers are running
```bash
docker compose ps
```

Access swagger documentation
auth service: http://localhost:8080/apidocs/ 
url shortening service: http://localhost:8101/apidocs/
