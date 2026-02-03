import jwt
import datetime
from functools import wraps
from flask import request, jsonify, make_response
from config import Config

# Secret key for encoding/decoding tokens
# In production, this should be in an environment variable
SECRET_KEY = "super_secret_smart_retail_key" 

# Mock Database for Demo
# Format: email: password
USERS = {
    "admin": "admin",
    "security": "admin"
}

def token_required(f):
    """
    Decorator to protect routes. 
    Mobile app must send 'x-access-token' in headers.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is passed in headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            # Decode and validate token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def login_user():
    """
    Handles user login and generates JWT token.
    """
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # Check credentials
    if auth.username in USERS and USERS[auth.username] == auth.password:
        # Generate Token (Valid for 24 hours)
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

# Install PyJWT package
# !pip install PyJWT