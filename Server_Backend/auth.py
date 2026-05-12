import jwt
import datetime
from functools import wraps
from flask import request, jsonify, make_response

# Secret key for encoding/decoding tokens
SECRET_KEY = "super_secret_smart_retail_key" 

# Mock Database for Demo
USERS = {
    "admin": "admin",
    "security": "admin"
}

def token_required(f):
    """Decorator to protect routes. Mobile app must send 'x-access-token'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def login_user():
    """Handles user login and generates JWT token."""
    print("\n[DEBUG] --- LOGIN ATTEMPT RECEIVED ---")
    
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        print("[ERROR] Missing Auth Header or Credentials")
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    print(f"[DEBUG] Attempting login for user: '{auth.username}'")

    if auth.username in USERS and USERS[auth.username] == auth.password:
        print("[SUCCESS] Credentials matched! Generating Token...")
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({'token': token})

    print(f"[ERROR] Invalid credentials for '{auth.username}'")
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})