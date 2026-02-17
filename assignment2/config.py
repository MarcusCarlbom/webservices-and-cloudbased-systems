import os

class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27420")
    MONGO_DB = os.environ.get("MONGO_DB", "url_shortener")
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"