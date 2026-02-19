from flask import Blueprint, request, jsonify
from services.jwt_service import create_token, verify_token
import hashlib


auth_blueprint = Blueprint('auth', __name__)
_repository = None

def init_controller(repository):
    global _repository
    _repository = repository


@auth_blueprint.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: User credentials for registration
        required: true
        schema:
          $ref: '#/definitions/UserInput'
    responses:
      201:
        description: User created successfully
      400:
        description: Bad request - Username or password missing
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Username already exists
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if _repository.find_by_username(username):
        return "duplicate", 409

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    _repository.create(username, hashed_password)
    return jsonify({"message": "User created successfully"}), 201


@auth_blueprint.route('/users', methods=['PUT'])
def update_password():
    """
    Update a user's password
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: Username with old and new password
        required: true
        schema:
          $ref: '#/definitions/PasswordUpdateInput'
    responses:
      200:
        description: Password updated successfully
      400:
        description: Bad request - Missing required fields
        schema:
          $ref: '#/definitions/ErrorResponse'
      403:
        description: Forbidden - Invalid credentials
    """
    data = request.get_json()
    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not username or not old_password or not new_password:
        return jsonify({"error": "Username, old password and new password are required"}), 400
    
    user = _repository.find_by_username(username)
    hashed_old = hashlib.sha256(old_password.encode()).hexdigest()
    if not user or user.password != hashed_old:
        return "forbidden", 403
    
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    _repository.update_password(username, hashed_new_password)
    return "", 200


@auth_blueprint.route('/users/login', methods=['POST'])
def login():
    """
    Login and receive a JWT
    ---
    tags:
      - Auth
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: User credentials for login
        required: true
        schema:
          $ref: '#/definitions/UserInput'
    responses:
      200:
        description: Login successful, returns a JWT token
        schema:
          $ref: '#/definitions/TokenResponse'
      403:
        description: Forbidden, Invalid username or password
    """
    data = request.get_json()
    
    username = data.get("username")
    password = data.get("password")
    
    user = _repository.find_by_username(username)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not user or user.password != hashed_password:
        return "forbidden", 403
    
    token = create_token(username)
    return jsonify({"token": token}), 200

@auth_blueprint.route('/users/validate', methods=['POST'])
def validate_token():
    """
    Validate a JWT token
    ---
    tags:
      - Auth
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JWT token to validate
        required: true
        schema:
          $ref: '#/definitions/TokenValidateInput'
    responses:
      200:
        description: Token is valid, returns username
        schema:
          $ref: '#/definitions/ValidateResponse'
      403:
        description: Forbidden, token is invalid or expired
    """
    data = request.get_json()
    token = data.get("token")
    if not token:
        return "forbidden", 403
    username = verify_token(token)
    if not username:
        return "forbidden", 403
    return jsonify({"username": username}), 200