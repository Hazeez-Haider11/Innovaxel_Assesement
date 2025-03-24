from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:"my_username"@localhost/url_shortener'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    access_count = db.Column(db.Integer, default=0)

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def create_short_url():
    data = request.json
    if 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    short_code = generate_short_code()
    new_url = URL(original_url=data['url'], short_code=short_code)
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({
        "id": new_url.id,
        "url": new_url.original_url,
        "shortCode": new_url.short_code,
        "createdAt": new_url.created_at,
        "updatedAt": new_url.updated_at
    }), 201

@app.route('/shorten/<short_code>', methods=['GET'])
def get_original_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        url.access_count += 1
        db.session.commit()
        return redirect(url.original_url)
    return jsonify({"error": "Short URL not found"}), 404

@app.route('/shorten/<short_code>', methods=['PUT'])
def update_short_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if not url:
        return jsonify({"error": "Short URL not found"}), 404
    
    data = request.json
    if 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url.original_url = data['url']
    db.session.commit()
    
    return jsonify({
        "id": url.id,
        "url": url.original_url,
        "shortCode": url.short_code,
        "createdAt": url.created_at,
        "updatedAt": url.updated_at
    })

@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_short_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if not url:
        return jsonify({"error": "Short URL not found"}), 404
    
    db.session.delete(url)
    db.session.commit()
    
    return '', 204

@app.route('/shorten/<short_code>/stats', methods=['GET'])
def get_url_stats(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if not url:
        return jsonify({"error": "Short URL not found"}), 404
    
    return jsonify({
        "id": url.id,
        "url": url.original_url,
        "shortCode": url.short_code,
        "createdAt": url.created_at,
        "updatedAt": url.updated_at,
        "accessCount": url.access_count
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)