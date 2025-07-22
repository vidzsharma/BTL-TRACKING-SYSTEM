import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, g
from functools import wraps
import json
from backend.db import get_db_connection
from config import Config

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, password):
    """Verify password against stored hash"""
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def create_token(user_id, username, role):
    """Create JWT token with user information"""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_location():
    """Get user location from request headers or IP"""
    # In a real implementation, you would use a geolocation service
    # For now, we'll return a default location
    return {
        "latitude": 28.6139,  # Default to Delhi coordinates
        "longitude": 77.2090,
        "location_name": "Delhi, India"
    }

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, password_hash, email, role, team_leader_id
            FROM users 
            WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        if user and check_password(user['password_hash'], password):
            return dict(user)
        return None
        
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        conn.close()

def login_user(username, password, request_data):
    """Complete login process with tracking"""
    user = authenticate_user(username, password)
    if not user:
        return None, "Invalid credentials"
    
    # Create token
    token = create_token(user['id'], user['username'], user['role'])
    
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "team_leader_id": user['team_leader_id']
        }
    }, "Login successful"

def require_auth(f):
    """Decorator to require authentication and set current user context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"message": "Invalid or expired token"}), 401
        
        # Get user details from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, role, team_leader_id, is_active
            FROM users 
            WHERE id = ? AND is_active = 1
        """, (payload['user_id'],))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"message": "User not found or inactive"}), 401
        
        # Set current user in Flask's g object
        g.current_user = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'team_leader_id': user['team_leader_id']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return jsonify({"message": "Authentication required"}), 401
            
            user_role = g.current_user.get('role')
            if user_role != required_role and user_role != 'admin':
                return jsonify({"message": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin_or_team_leader(f):
    """Decorator to require admin or team leader role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({"message": "Authentication required"}), 401
        
        user_role = g.current_user.get('role')
        if user_role not in ['admin', 'team_leader']:
            return jsonify({"message": "Insufficient permissions"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, role, team_leader_id, is_active
            FROM users 
            WHERE id = ?
        """, (user_id,))
        
        return cursor.fetchone()
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()

def get_team_members(team_leader_id):
    """Get all team members for a team leader"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, role, created_at
            FROM users 
            WHERE team_leader_id = ? AND is_active = 1
        """, (team_leader_id,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting team members: {e}")
        return []
    finally:
        conn.close()

def get_team_leader_id(user_id):
    """Get team leader ID for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT team_leader_id
            FROM users 
            WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        return result['team_leader_id'] if result else None
        
    except Exception as e:
        print(f"Error getting team leader: {e}")
        return None
    finally:
        conn.close() 