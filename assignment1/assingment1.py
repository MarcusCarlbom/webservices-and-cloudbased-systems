from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

url_database = {}

@app.route('/', methods=['POST'])
def shorten_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    new_id = generate_id()
    url_database[new_id] = url
    return jsonify({'id': new_id}), 201

# Get only stored URL ids and not the correlated links, per specification in assignment. 
@app.route('/', methods=['GET'])
def get_urls():
    return jsonify(list(url_database.keys())), 200

@app.route('/<id>', methods=['GET'])
def redirect_url(id):
    url = url_database.get(id)
    if not url:
        return '', 404
    return redirect(url, code=301)

@app.route('/<id>', methods=['PUT'])
def update_url(id):
    data = request.get_json()
    new_url = data.get('url')
    if data.get('url') is None:
        return jsonify({'error': 'No URL provided'}), 400
    if id not in url_database:
        return jsonify({'error': 'ID not found'}), 404
    url_database[id] = new_url
    return '', 200

@app.route('/<id>', methods=['DELETE'])
def delete_url(id):
    if id not in url_database:
        return jsonify({'error': 'ID not found'}), 404
    del url_database[id]
    return '', 204

@app.route('/', methods=['DELETE'])
def invalid_delete():
    return '', 404