from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash
from backend.auth import check_password
import pandas as pd
import os
from datetime import datetime, date
import requests
from config import Config
from backend.db import (
    get_user_by_username, get_user_by_id, create_user, 
    update_user_login, log_login, get_team_members, get_all_users, get_db_connection
)
from backend.auth import require_auth, require_role, require_admin_or_team_leader
from backend.mis import get_mis_data, get_mis_statistics
from backend.progress import create_lead, get_user_leads, update_lead_progress

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
        if not user or not check_password(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get location data (optional - don't fail if this doesn't work)
        location = "Unknown"
        try:
            response = requests.get(Config.LOCATION_API_URL, timeout=2)
            if response.status_code == 200:
                location_data = response.json()
                location = f"{location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}"
        except Exception as e:
            # Log the error but don't fail the login
            print(f"Location API error (non-critical): {e}")
            location = "Unknown"
        
        # Update login info
        try:
            update_user_login(user['id'], location)
            log_login(user['id'], request.remote_addr, location, request.headers.get('User-Agent', ''))
        except Exception as e:
            # Log the error but don't fail the login
            print(f"Login tracking error (non-critical): {e}")
        
        # Create JWT token
        from backend.auth import create_token
        access_token = create_token(user['id'], user['username'], user['role'])
        
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
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
@require_auth
@require_role('admin')
def register():
    """Register new user (Admin only)"""
    try:
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
@require_auth
def get_users():
    """Get users based on role hierarchy"""
    try:
        current_user = g.current_user
        
        if current_user['role'] == 'admin':
            users = get_all_users()
        elif current_user['role'] == 'team_leader':
            users = get_team_members(current_user['id'])
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
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        current_user = g.current_user
        
        return jsonify({
            'id': current_user['id'],
            'username': current_user['username'],
            'email': current_user['email'],
            'role': current_user['role'],
            'team_leader_id': current_user['team_leader_id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/mis-files', methods=['GET'])
@require_auth
def get_mis_files():
    """Get uploaded MIS files based on role hierarchy"""
    try:
        current_user = g.current_user
        
        # Get MIS data based on role
        mis_data = get_mis_data(current_user['id'], current_user['role'], current_user['team_leader_id'])
        
        file_list = []
        for file in mis_data:
            file_list.append({
                'id': file['id'],
                'file_name': file['file_name'],
                'upload_date': file['upload_date'],
                'created_by': file['created_by'],
                'total_records': file['total_records'],
                'processed_records': file['processed_records'],
                'status': file['status']
            })
        
        return jsonify({'files': file_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mis-data', methods=['GET'])
@require_auth
def get_mis_data_route():
    """Get actual MIS data records based on role hierarchy"""
    try:
        current_user = g.current_user
        
        # Get MIS data based on role
        mis_data = get_mis_data(current_user['id'], current_user['role'], current_user['team_leader_id'])
        
        # Convert SQLite Row objects to dictionaries for JSON serialization
        mis_data_dict = []
        for row in mis_data:
            mis_data_dict.append(dict(row))
        
        return jsonify({'data': mis_data_dict}), 200
        
    except Exception as e:
        print(f"Error in get_mis_data_route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/leads', methods=['GET'])
@require_auth
def get_leads():
    """Get leads based on role hierarchy"""
    try:
        current_user = g.current_user
        status_filter = request.args.get('status')
        team_member = request.args.get('team_member')  # For team leaders to filter by member
        
        # Get leads based on role
        leads = get_user_leads(
            current_user['id'], 
            current_user['role'], 
            current_user['team_leader_id'],
            status_filter,
            team_member
        )
        
        return jsonify({'leads': leads}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/leads', methods=['POST'])
@require_auth
def create_new_lead():
    """Create a new lead"""
    try:
        current_user = g.current_user
        data = request.get_json()
        
        # Extract lead data
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        customer_email = data.get('customer_email')
        bank_name = data.get('bank_name')
        campaign_tag = data.get('campaign_tag')
        
        if not customer_name:
            return jsonify({'error': 'Customer name is required'}), 400
        
        # Create lead with created_by field
        success, result = create_lead(
            current_user['id'],
            campaign_tag,
            customer_name,
            customer_phone,
            customer_email,
            bank_name,
            current_user['username']  # created_by field
        )
        
        if success:
            return jsonify(result), 201
        else:
            return jsonify({'error': result}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/leads/<int:lead_id>/progress', methods=['PUT'])
@require_auth
def update_lead_progress_route(lead_id):
    """Update lead progress"""
    try:
        current_user = g.current_user
        data = request.get_json()
        
        progress_status = data.get('status')
        progress_notes = data.get('notes')
        
        if not progress_status:
            return jsonify({'error': 'Status is required'}), 400
        
        # Update lead progress
        success, result = update_lead_progress(
            lead_id,
            current_user['id'],
            progress_status,
            progress_notes
        )
        
        if success:
            return jsonify({'message': result}), 200
        else:
            return jsonify({'error': result}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/statistics', methods=['GET'])
@require_auth
def get_progress_statistics():
    """Get progress statistics based on role hierarchy"""
    try:
        current_user = g.current_user
        days = request.args.get('days', 30, type=int)
        
        from backend.progress import get_progress_statistics as get_stats
        stats = get_stats(
            current_user['id'],
            current_user['role'],
            current_user['team_leader_id'],
            days
        )
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/mis-analytics', methods=['GET'])
@require_auth
def get_mis_analytics():
    """Get comprehensive MIS analytics"""
    try:
        current_user = g.current_user
        days = request.args.get('days', 30, type=int)
        
        from backend.progress import get_mis_analytics
        analytics = get_mis_analytics(
            current_user['id'],
            current_user['role'],
            current_user['team_leader_id'],
            days
        )
        
        return jsonify({'success': True, 'data': analytics}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/progress/login-stats', methods=['GET'])
@require_auth
def get_login_stats():
    """Get user login statistics including location and time"""
    try:
        current_user = g.current_user
        days = request.args.get('days', 30, type=int)
        
        from backend.progress import get_user_login_stats
        login_stats = get_user_login_stats(
            current_user['id'],
            current_user['role'],
            current_user['team_leader_id'],
            days
        )
        
        return jsonify({'success': True, 'data': login_stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/progress/lead-analytics', methods=['GET'])
@require_auth
def get_lead_analytics():
    """Get lead analytics grouped by application status"""
    try:
        current_user = g.current_user
        days = request.args.get('days', 30, type=int)
        
        from backend.progress import get_lead_analytics_by_status
        lead_analytics = get_lead_analytics_by_status(
            current_user['id'],
            current_user['role'],
            current_user['team_leader_id'],
            days
        )
        
        return jsonify({'success': True, 'data': lead_analytics}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/team/members', methods=['GET'])
@require_auth
def get_team_members_route():
    """Get team members (Admin and Team Leaders only)"""
    try:
        current_user = g.current_user
        
        if current_user['role'] not in ['admin', 'team_leader']:
            return jsonify({'error': 'Access denied'}), 403
        
        if current_user['role'] == 'admin':
            # Admin can see all users
            users = get_all_users()
        else:
            # Team leader can see their team members
            users = get_team_members(current_user['id'])
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user['created_at'],
                'is_active': user['is_active']
            })
        
        return jsonify({'team_members': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/team/detailed-stats', methods=['GET'])
@require_auth
def get_team_detailed_stats():
    """Get detailed statistics for team members (Team Leaders only)"""
    try:
        current_user = g.current_user
        
        if current_user['role'] != 'team_leader':
            return jsonify({'error': 'Access denied. Team Leaders only.'}), 403
        
        days = request.args.get('days', 30, type=int)
        
        from backend.progress import get_team_member_detailed_stats
        detailed_stats = get_team_member_detailed_stats(
            current_user['id'],
            days
        )
        
        return jsonify({'success': True, 'data': detailed_stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 