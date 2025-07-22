import requests
import streamlit as st
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

def get_auth_headers():
    """Get authentication headers with JWT token"""
    token = st.session_state.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return {'Content-Type': 'application/json'}

def api_request(method, endpoint, data=None, files=None, params=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = get_auth_headers()
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            if files:
                # Remove Content-Type for file uploads
                headers.pop('Content-Type', None)
                response = requests.post(url, headers=headers, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return False, "Invalid HTTP method"
        
        if response.status_code == 401:
            # Token expired or invalid
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.rerun()
        
        if response.status_code >= 200 and response.status_code < 300:
            return True, response.json()
        else:
            error_data = response.json() if response.content else {}
            return False, error_data.get('error', f'HTTP {response.status_code}')
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if the backend is running."
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def login_user(username, password):
    """Login user and store token"""
    success, response = api_request('POST', '/login', {
        'username': username,
        'password': password
    })
    
    if success:
        st.session_state['access_token'] = response['access_token']
        st.session_state['user'] = response['user']
        st.session_state['logged_in'] = True
        return True, "Login successful"
    else:
        return False, response

def logout_user():
    """Logout user and clear session"""
    st.session_state.clear()
    st.success("Logged out successfully")

def get_user_profile():
    """Get current user profile"""
    success, response = api_request('GET', '/profile')
    if success:
        return response
    return None

def get_users():
    """Get all users (Admin/Team Leader only)"""
    success, response = api_request('GET', '/users')
    if success:
        return response.get('users', [])
    return []



def create_user(user_data):
    """Create new user (Admin only)"""
    success, response = api_request('POST', '/register', user_data)
    return success, response

# Dashboard Helper Functions
def get_dashboard_stats(team_member=None):
    """Get dashboard statistics with optional team member filtering"""
    params = {}
    if team_member and team_member != 'All Team Members':
        params['team_member'] = team_member
    
    success, response = api_request('GET', '/progress/statistics', params=params)
    if success:
        return response
    return {}

def create_performance_chart(data):
    """Create performance chart"""
    fig = go.Figure()
    
    # Add traces for different metrics
    fig.add_trace(go.Scatter(
        x=data.get('dates', []),
        y=data.get('leads_contacted', []),
        mode='lines+markers',
        name='Leads Contacted',
        line=dict(color='#1f77b4')
    ))
    
    fig.add_trace(go.Scatter(
        x=data.get('dates', []),
        y=data.get('leads_converted', []),
        mode='lines+markers',
        name='Leads Converted',
        line=dict(color='#2ca02c')
    ))
    
    fig.update_layout(
        title='Performance Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Leads',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_conversion_chart(conversion_data):
    """Create conversion funnel chart"""
    fig = go.Figure(go.Funnel(
        y=['Total Leads', 'Contacted', 'Interested', 'Applications', 'Approved'],
        x=conversion_data,
        textinfo="value+percent initial"
    ))
    
    fig.update_layout(
        title='Lead Conversion Funnel',
        template='plotly_white'
    )
    
    return fig

# Utility Functions
def format_date(date_string):
    """Format date string for display"""
    try:
        if isinstance(date_string, str):
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d %H:%M')
        return date_string
    except:
        return date_string

def format_number(number):
    """Format number for display"""
    try:
        return f"{number:,}"
    except:
        return str(number)

def get_role_display_name(role):
    """Get display name for role"""
    role_names = {
        'admin': 'Administrator',
        'team_leader': 'Team Leader',
        'user': 'User'
    }
    return role_names.get(role, role.title())



def display_success_message(message):
    """Display success message"""
    st.success(message)

def display_error_message(message):
    """Display error message"""
    st.error(message)

def display_info_message(message):
    """Display info message"""
    st.info(message)

# Data Retrieval Functions
def get_mis_data():
    """Get MIS data based on user role"""
    success, response = api_request('GET', '/mis-data')
    if success:
        return response.get('data', [])
    return []

def get_leads_data(status_filter=None, team_member=None):
    """Get leads data with optional filtering"""
    params = {}
    if status_filter:
        params['status'] = status_filter
    if team_member and team_member != 'All Team Members':
        params['team_member'] = team_member
    
    success, response = api_request('GET', '/leads', params=params)
    if success:
        return response.get('leads', [])
    return []

def get_performance_data(days=30, team_member=None):
    """Get performance data with optional team member filtering"""
    params = {'days': days}
    if team_member and team_member != 'All Team Members':
        params['team_member'] = team_member
    
    success, response = api_request('GET', '/team/members', params=params)
    if success:
        return response.get('team_members', [])
    return []

def get_team_members():
    """Get team members (Admin/Team Leader only)"""
    success, response = api_request('GET', '/team/members')
    if success:
        return response.get('team_members', [])
    return []

# User Management Functions
def get_user_role():
    """Get current user role"""
    user = st.session_state.get('user')
    if user:
        return user.get('role', 'user')
    return 'user'

def get_current_user():
    """Get current user information"""
    return st.session_state.get('user', {})

def get_user_id():
    """Get current user ID"""
    user = st.session_state.get('user')
    if user:
        return user.get('id')
    return None

def get_team_leader_id():
    """Get current user's team leader ID"""
    user = st.session_state.get('user')
    if user:
        return user.get('team_leader_id')
    return None

def format_datetime(dt_string):
    """Format datetime string for display"""
    try:
        if isinstance(dt_string, str):
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string
    except:
        return dt_string

def create_metrics_dataframe(data):
    """Create metrics dataframe for display"""
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
    
    if 'updated_at' in df.columns:
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['updated_at'] = df['updated_at'].dt.strftime('%Y-%m-%d %H:%M')
    
    if 'upload_date' in df.columns:
        df['upload_date'] = pd.to_datetime(df['upload_date'])
        df['upload_date'] = df['upload_date'].dt.strftime('%Y-%m-%d %H:%M')
    
    return df

# Lead Management Functions
def create_lead(lead_data):
    """Create new lead"""
    # For now, return success - implement when leads API is ready
    return True, {"lead_id": "DEMO001", "message": "Lead created successfully"}

def update_lead_progress(lead_id, progress_data):
    """Update lead progress"""
    # For now, return success - implement when leads API is ready
    return True, "Lead updated successfully"

def get_lead_details(lead_id):
    """Get lead details"""
    # For now, return None - implement when leads API is ready
    return None

def get_lead_status_options():
    """Get lead status options for dropdown"""
    return ['new', 'in-progress', 'closed', 'rejected']

def check_permissions(required_role):
    """Check if user has required role"""
    user_role = get_user_role()
    if user_role == 'admin':
        return True
    return user_role == required_role

# Session Management
def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('logged_in', False)

def require_role(required_role):
    """Require specific role to access page"""
    if not check_authentication():
        st.error("Please login to access this page")
        st.stop()

    user_role = st.session_state.get('user', {}).get('role')
    
    if user_role != required_role:
        st.error(f"Access denied. {get_role_display_name(required_role)} role required.")
        st.stop()

def require_roles(allowed_roles):
    """Require one of the specified roles to access page"""
    if not check_authentication():
        st.error("Please login to access this page")
        st.stop()
    
    user_role = st.session_state.get('user', {}).get('role')
    
    if user_role not in allowed_roles:
        role_names = [get_role_display_name(role) for role in allowed_roles]
        st.error(f"Access denied. One of these roles required: {', '.join(role_names)}")
        st.stop() 

# Analytics Functions
def get_mis_analytics():
    """Get comprehensive MIS analytics"""
    user_id = get_user_id()
    user_role = get_user_role()
    team_leader_id = get_team_leader_id()
    
    success, response = api_request('GET', '/progress/mis-analytics', params={
        'user_id': user_id,
        'role': user_role,
        'team_leader_id': team_leader_id
    })
    
    if success:
        return response.get('data', {})
    return {}

def get_login_stats():
    """Get user login statistics including location and time (Team Leaders and Admins only)"""
    user_id = get_user_id()
    user_role = get_user_role()
    team_leader_id = get_team_leader_id()
    
    # Only team leaders and admins can see login statistics
    if user_role not in ['admin', 'team_leader']:
        return []
    
    success, response = api_request('GET', '/progress/login-stats', params={
        'user_id': user_id,
        'role': user_role,
        'team_leader_id': team_leader_id
    })
    
    if success:
        return response.get('data', [])
    return []

def get_lead_analytics():
    """Get lead analytics grouped by application status"""
    user_id = get_user_id()
    user_role = get_user_role()
    team_leader_id = get_team_leader_id()
    
    success, response = api_request('GET', '/progress/lead-analytics', params={
        'user_id': user_id,
        'role': user_role,
        'team_leader_id': team_leader_id
    })
    
    if success:
        return response.get('data', [])
    return []

def get_team_detailed_stats():
    """Get detailed team member statistics (Team Leaders only)"""
    success, response = api_request('GET', '/team/detailed-stats')
    if success:
        return response.get('data', [])
    return [] 