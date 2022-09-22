from flask import jsonify
from app import app

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'not found'}), 404
