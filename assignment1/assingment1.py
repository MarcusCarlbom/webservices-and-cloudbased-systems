from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

url_database = {}
id_counter = 0

# Based on the link https://mojoauth.com/binary-encoding-decoding/base62-with-python#encoding-data-to-base62
def base62_encode(num):
    if num == 0:
        return '0'
    base62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    while num > 0:
        remainder = num % 62  
        result.append(base62[remainder])
        num = num // 62
    return ''.join(reversed(result))


def generate_id():
    global id_counter
    id_counter += 1
    return base62_encode(id_counter)


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
    if id not in url_database:
        return '', 404
    if new_url is None:
        return jsonify({'error': 'No URL provided'}), 400
    url_database[id] = new_url
    return '', 200

@app.route('/<id>', methods=['DELETE'])
def delete_url(id):
    if id not in url_database:
        return '', 404
    del url_database[id]
    return '', 204

@app.route('/', methods=['DELETE'])
def invalid_delete():
    return '', 404