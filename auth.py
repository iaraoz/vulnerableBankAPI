import jwt
import datetime
from functools import wraps
from flask import request, jsonify


JWT_SECRET = "very_weak_secret_key_that_should_never_be_used_in_production"


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        
    }
   
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def decode_token(token):
    try:
    
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.InvalidTokenError:
        return None

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            token = auth_header.split()[1]
        except IndexError:
            return jsonify({"error": "Invalid token format"}), 401
        
        user_id = decode_token(token)
        if not user_id:
           
            return jsonify({"error": "Invalid token. Token could not be decoded or has expired."}), 401
        
        return f(*args, **kwargs)
    
    return decorated
