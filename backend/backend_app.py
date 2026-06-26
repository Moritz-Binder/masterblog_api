from flask import Flask, jsonify, request
from flask_cors import CORS
import re
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        if request.get_json() is None:
            return "Media type must be json format.", 415
        
        data = request.get_json()
        if data.get('title') is None or data.get('content') is None:
            return "Json must entail title and content key.", 400
        
        title = data.get('title')
        content = data.get('content')

        if not isinstance(title, str) or not isinstance(content, str):
            return "title and content values must be strings.", 422

        new_post = {
            'id': len(POSTS) + 1,
            'title': title,
            'content': content
        }
        POSTS.append(new_post)
        return jsonify(POSTS), 201

    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc').lower()

    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": f"Invalid sort field '{sort_field}'. Allowed fields are 'title' or 'content'."}), 400
            
        if direction not in ['asc', 'desc']:
            return jsonify({"error": f"Invalid direction '{direction}'. Allowed values are 'asc' or 'desc'."}), 400

        is_reverse = (direction == 'desc')
        
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_field].lower(), reverse=is_reverse)
        return jsonify(sorted_posts)

    return jsonify(POSTS)

@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete(id):
    global POSTS
    if not isinstance(id, int):
        return "id must be a integer.", 422
    if next((post['id'] for post in POSTS if post['id']==id), None) is None:
        return f"Post with ID {id} not found.", 404
    POSTS=[post for post in POSTS if post['id']!=id]
    message= {
        "message": f"Post with id {id} has been deleted successfully."
    }
    return jsonify(message), 200

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update(id):
    global POSTS
    if not isinstance(id, int):
        return "id must be a integer.", 422
    if next((post['id'] for post in POSTS if post['id']==id), None) is None:
        return f"Post with ID {id} not found.", 404
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    old_post = next((post for post in POSTS if post['id']==id))
    if title is not None:
        old_post['title']=title
    if content is not None:
        old_post['content']=content
    
    POSTS=[post for post in POSTS if post['id']!=id]
    POSTS.append(old_post)
    return jsonify(old_post), 200

@app.route('/api/posts/search', methods=['GET'])
def search():
    title_query = request.args.get('title', '')
    content_query = request.args.get('content', '')

    filtered_posts = []
    
    for post in POSTS:
        title_match = False
        content_match = False

        if title_query:
            title_match = re.search(title_query, post['title'], re.IGNORECASE) is not None
            
        if content_query:
            content_match = re.search(content_query, post['content'], re.IGNORECASE) is not None

        if title_match or content_match:
            filtered_posts.append(post)

    return jsonify(filtered_posts), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
