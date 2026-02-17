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
    data = request.get_json()
    token = data.get("token")
    if not token:
        return "forbidden", 403
    username = verify_token(token)
    if not username:
        return "forbidden", 403
    return jsonify({"username": username}), 200