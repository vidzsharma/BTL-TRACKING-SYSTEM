import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
import json
from backend.db import get_db_cursor, close_db_connection
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

def track_login(user_id, request_data):
    """Track user login with location and time"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return None
    
    try:
        # Get location data
        location_data = get_user_location()
        
        # Get IP address
        ip_address = request_data.headers.get('X-Forwarded-For', 
                    request_data.headers.get('X-Real-IP', 
                    request_data.remote_addr))
        
        # Get user agent
        user_agent = request_data.headers.get('User-Agent', '')
        
        # Insert login tracking record
        cursor.execute("""
            INSERT INTO login_tracking 
            (user_id, ip_address, user_agent, location_data, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING tracking_id
        """, (
            user_id, 
            ip_address, 
            user_agent, 
            json.dumps(location_data),
            location_data['latitude'],
            location_data['longitude']
        ))
        
        tracking_id = cursor.fetchone()['tracking_id']
        conn.commit()
        return tracking_id
        
    except Exception as e:
        print(f"Error tracking login: {e}")
        conn.rollback()
        return None
    finally:
        close_db_connection(conn, cursor)

def track_logout(user_id):
    """Track user logout time"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return False
    
    try:
        cursor.execute("""
            UPDATE login_tracking 
            SET logout_time = CURRENT_TIMESTAMP
            WHERE user_id = %s AND logout_time IS NULL
        """, (user_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error tracking logout: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn, cursor)

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return None
    
    try:
        cursor.execute("""
            SELECT user_id, username, password_hash, email, role, team_leader_id
            FROM users 
            WHERE username = %s AND is_active = TRUE
        """, (username,))
        
        user = cursor.fetchone()
        if user and check_password(user['password_hash'], password):
            return dict(user)
        return None
        
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        close_db_connection(conn, cursor)

def login_user(username, password, request_data):
    """Complete login process with tracking"""
    user = authenticate_user(username, password)
    if not user:
        return None, "Invalid credentials"
    
    # Track login
    tracking_id = track_login(user['user_id'], request_data)
    
    # Create token
    token = create_token(user['user_id'], user['username'], user['role'])
    
    return {
        "token": token,
        "user": {
            "user_id": user['user_id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "team_leader_id": user['team_leader_id']
        },
        "tracking_id": tracking_id
    }, "Login successful"

def require_auth(f):
    """Decorator to require authentication"""
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
        
        # Add user info to request
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({"message": "Authentication required"}), 401
            
            user_role = request.current_user.get('role')
            if user_role != required_role and user_role != 'admin':
                return jsonify({"message": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_by_id(user_id):
    """Get user by ID"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return None
    
    try:
        cursor.execute("""
            SELECT user_id, username, email, role, team_leader_id, is_active
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        
        return cursor.fetchone()
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        close_db_connection(conn, cursor)

def get_team_members(team_leader_id):
    """Get all team members for a team leader"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return []
    
    try:
        cursor.execute("""
            SELECT user_id, username, email, role, created_at
            FROM users 
            WHERE team_leader_id = %s AND is_active = TRUE
        """, (team_leader_id,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting team members: {e}")
        return []
    finally:
        close_db_connection(conn, cursor) 