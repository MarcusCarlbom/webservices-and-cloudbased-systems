from flask import Flask
from flasgger import Swagger

from config import Config
from repositories.user_repository import UserRepository
from controllers.auth_controller import auth_blueprint, init_controller

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
        "title": "Authentication Service API",
        "description": "User authentication service with JWT support.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Auth",
            "description": "User registration, login and password management"
        }
    ],
    "definitions": {
        "UserInput": {
            "type": "object",
            "required": ["username", "password"],
            "properties": {
                "username": {
                    "type": "string",
                    "example": "marcus"
                },
                "password": {
                    "type": "string",
                    "example": "mypassword"
                }
            }
        },
        "TokenResponse": {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "example": "eyJhbGciOiJIUzI1NiJ9..."
                }
            }
        },
        "PasswordUpdateInput": {
            "type": "object",
            "required": ["username", "old_password", "new_password"],
            "properties": {
                "username": {
                    "type": "string",
                    "example": "myusername"
                },
                "old_password": {
                    "type": "string",
                    "example": "mypassword"
                },
                "new_password": {
                    "type": "string",
                    "example": "mynewpassword"
                }
            }
        },
        "TokenValidateInput": {
            "type": "object",
            "required": ["token"],
            "properties": {
                "token": {
                    "type": "string",
                    "example": "eyJhbGciOiJIUzI1NiJ9..."
                }
            }
        },
        "ValidateResponse": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "example": "myusername"
                }
            }
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Username and password are required",
                    "description": "Error message describing what went wrong"
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

repository = UserRepository(mongo_uri=Config.MONGO_URI, db_name=Config.MONGO_DB)
init_controller(repository)
app.register_blueprint(auth_blueprint)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8101)
