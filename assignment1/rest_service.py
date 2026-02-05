from flask import Flask
from flasgger import Swagger

from config import Config
from repositories.url_repository import URLRepository
from controllers.url_controller import url_blueprint, init_controller

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "URL Shortener API",
        "description": "A minimal URL shortening service built with Flask and MongoDB. "
                       "Create short URLs, retrieve them, update them, or delete them.",
        "version": "1.0.0",
        "contact": {
            "name": "API Support"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "URLs",
            "description": "Operations for managing shortened URLs"
        }
    ],
    "definitions": {
        "URLInput": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {
                    "type": "string",
                    "example": "https://www.google.com",
                    "description": "The original URL to be shortened. Must be a valid HTTP/HTTPS URL."
                }
            }
        },
        "URLCreatedResponse": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "example": "1",
                    "description": "The generated short ID for the URL"
                }
            }
        },
        "URLListResponse": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "example": ["1", "2", "3"]
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "No URL provided",
                    "description": "Error message describing what went wrong"
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# init repository with MongoDB connection
repository = URLRepository(mongo_uri=Config.MONGO_URI, db_name=Config.MONGO_DB)

# init controller with repository
init_controller(repository)

# register bp
app.register_blueprint(url_blueprint)


if __name__ == "__main__":
    app.run(debug=True)