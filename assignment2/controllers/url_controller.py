import re
from flask import Blueprint, request, jsonify, redirect
from repositories.url_repository import URLRepository

from services.auth_client import validate_token



url_blueprint = Blueprint("urls", __name__)

# repository instance is initialized by init_controller
_repository: URLRepository = None

def init_controller(repository: URLRepository) -> None:
    global _repository
    _repository = repository

def get_authenticated_user():
    token = request.headers.get("Authorization")
    if not token:
        return None
    return validate_token(token)


@url_blueprint.route("/", methods=["POST"])
def create_url():
    """
    Create a shortened URL
    ---
    tags:
      - URLs
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: URL to be shortened
        required: true
        schema:
          $ref: '#/definitions/URLInput'
    responses:
      201:
        description: URL successfully shortened
        schema:
          $ref: '#/definitions/URLCreatedResponse'
      400:
        description: Bad request - No URL provided or invalid URL
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    
    data = request.get_json()
    if not data or not data.get("value"):
        return jsonify({"error": "No URL provided"}), 400

    url = data["value"]
    
    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(url_pattern, url):
        return jsonify({"error": "Invalid URL format"}), 400
    
    model = _repository.create(url, username)
    return jsonify({"id": model.id}), 201


@url_blueprint.route("/", methods=["GET"])
def get_all_urls():
    """
    List all shortened URL IDs
    ---
    tags:
      - URLs
    produces:
      - application/json
    responses:
      200:
        description: List of all stored URL IDs
        schema:
          $ref: '#/definitions/URLListResponse'
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    ids = _repository.get_all_ids(username)
    return jsonify(ids), 200


@url_blueprint.route("/<url_id>", methods=["GET"])
def get_url(url_id: str):
    """
    Redirect to the original URL
    ---
    tags:
      - URLs
    parameters:
      - name: url_id
        in: path
        type: string
        required: true
        description: The short ID of the URL
        example: "1"
    responses:
      301:
        description: Redirect to the original URL
        headers:
          Location:
            type: string
            description: The original URL to redirect to
      404:
        description: URL not found
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    
    model = _repository.get_by_id(url_id)
    if model is None:
        return "", 404
    return jsonify({"value": model.url}), 301


@url_blueprint.route("/<url_id>", methods=["PUT"])
def update_url(url_id: str):
    """
    Update an existing shortened URL
    ---
    tags:
      - URLs
    consumes:
      - application/json
    parameters:
      - name: url_id
        in: path
        type: string
        required: true
        description: The short ID of the URL to update
        example: "1"
      - in: body
        name: body
        description: New URL to replace the existing one
        required: true
        schema:
          $ref: '#/definitions/URLInput'
    responses:
      200:
        description: URL successfully updated
      400:
        description: Bad request - No URL provided
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: URL not found
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    
    model = _repository.get_by_id(url_id)
    if not model:
        return "", 404
    if model.username != username:
        return "forbidden", 403
      
    data = request.get_json(force=True)
    if not data or data.get("value") is None:
        return jsonify({"error": "No URL provided"}), 400

    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(url_pattern, data["value"]):
        return jsonify({"error": "Invalid URL format"}), 400

    _repository.update(url_id, data["value"])
    return "", 200


@url_blueprint.route("/<url_id>", methods=["DELETE"])
def delete_url(url_id: str):
    """
    Delete a shortened URL
    ---
    tags:
      - URLs
    parameters:
      - name: url_id
        in: path
        type: string
        required: true
        description: The short ID of the URL to delete
        example: "1"
    responses:
      204:
        description: URL successfully deleted
      404:
        description: URL not found
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    model = _repository.get_by_id(url_id)
    if not model:
        return "", 404
    if model.username != username:
        return "forbidden", 403
    _repository.delete(url_id)
    return "", 204


@url_blueprint.route("/", methods=["DELETE"])
def delete_root():
    """
    Invalid delete operation (no ID specified)
    ---
    tags:
      - URLs
    responses:
      404:
        description: Not found - Cannot delete without specifying an ID
    """
    username = get_authenticated_user()
    if not username:
        return "forbidden", 403
    
    ids = _repository.get_all_ids(username)
    for url_id in ids:
        _repository.delete(url_id)
    
    return "", 404