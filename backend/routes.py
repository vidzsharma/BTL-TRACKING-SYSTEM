from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os
from datetime import datetime, date
import requests
from config import Config
from backend.db import (
    get_user_by_username, get_user_by_id, create_user, 
    update_user_login, log_login, get_team_members, get_all_users, get_db_connection
)

# Create Blueprint
app = Blueprint('api', __name__, url_prefix='/api')

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = get_user_by_username(username)
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get location data
        location = "Unknown"
        try:
            response = requests.get(Config.LOCATION_API_URL)
            if response.status_code == 200:
                location_data = response.json()
                location = f"{location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}"
        except:
            pass
        
        # Update login info
        update_user_login(user['id'], location)
        log_login(user['id'], request.remote_addr, location, request.headers.get('User-Agent', ''))
        
        # Create access token
        access_token = create_access_token(identity=str(user['id']))
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'team_leader_id': user['team_leader_id']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Register new user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(int(current_user_id))
        
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Only admins can register new users'}), 403
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'user')
        team_leader_id = data.get('team_leader_id')
        
        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400
        
        password_hash = generate_password_hash(password)
        user_id = create_user(username, password_hash, email, role, team_leader_id)
        
        if user_id:
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        else:
            return jsonify({'error': 'Username or email already exists'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (Admin/Team Leader only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(int(current_user_id))
        
        if current_user['role'] == 'admin':
            users = get_all_users()
        elif current_user['role'] == 'team_leader':
            users = get_team_members(int(current_user_id))
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'team_leader_id': user['team_leader_id'],
                'created_at': user['created_at'],
                'last_login': user['last_login'],
                'is_active': user['is_active']
            })
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = get_user_by_id(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'team_leader_id': user['team_leader_id'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-mis', methods=['POST'])
@jwt_required()
def upload_mis():
    """Upload MIS file"""
    try:
        current_user_id = int(get_jwt_identity())
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Only Excel files are allowed'}), 400
        
        # Create uploads directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process file
        try:
            df = pd.read_excel(file_path)
            total_records = len(df)
            
            # Here you would process the MIS data according to your requirements
            # For now, we'll just save the file info
            
            # Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mis_data (file_name, uploaded_by, total_records, processed_records, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, current_user_id, total_records, total_records, file_path))
            conn.commit()
            conn.close()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'total_records': total_records
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mis-files', methods=['GET'])
@jwt_required()
def get_mis_files():
    """Get uploaded MIS files"""
    try:
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(int(current_user_id))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if current_user['role'] == 'admin':
            cursor.execute('''
                SELECT m.*, u.username as uploaded_by_name
                FROM mis_data m
                JOIN users u ON m.uploaded_by = u.id
                ORDER BY m.upload_date DESC
            ''')
        else:
            cursor.execute('''
                SELECT m.*, u.username as uploaded_by_name
                FROM mis_data m
                JOIN users u ON m.uploaded_by = u.id
                WHERE m.uploaded_by = ?
                ORDER BY m.upload_date DESC
            ''', (current_user_id,))
        
        files = cursor.fetchall()
        conn.close()
        
        file_list = []
        for file in files:
            file_list.append({
                'id': file['id'],
                'file_name': file['file_name'],
                'upload_date': file['upload_date'],
                'uploaded_by': file['uploaded_by_name'],
                'total_records': file['total_records'],
                'processed_records': file['processed_records'],
                'status': file['status']
            })
        
        return jsonify({'files': file_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 