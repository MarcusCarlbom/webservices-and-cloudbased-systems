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

Or run the demo
```bash
chmod +x [PATH_TO_DIRECTORY]/assignment3/demo.sh)
```

Access swagger documentation
exposed nginx proxy http://loclahost:8080/apidocs/
