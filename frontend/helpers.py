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

def api_request(method, endpoint, data=None, files=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = get_auth_headers()
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
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

def upload_mis_file(file):
    """Upload MIS file"""
    files = {'file': file}
    success, response = api_request('POST', '/upload-mis', files=files)
    return success, response

def get_mis_files():
    """Get uploaded MIS files"""
    success, response = api_request('GET', '/mis-files')
    if success:
        return response.get('files', [])
    return []

def create_user(user_data):
    """Create new user (Admin only)"""
    success, response = api_request('POST', '/register', user_data)
    return success, response

# Dashboard Helper Functions
def get_dashboard_stats():
    """Get dashboard statistics"""
    # This would be implemented based on your specific requirements
    # For now, returning mock data
    return {
        'total_leads': 150,
        'active_leads': 45,
        'converted_leads': 23,
        'conversion_rate': 15.3,
        'team_performance': 85.7
    }

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

def validate_file_upload(file):
    """Validate uploaded file"""
    if file is None:
        return False, "Please select a file"
    
    allowed_extensions = {'.xlsx', '.xls'}
    file_extension = file.name.lower()
    
    if not any(file_extension.endswith(ext) for ext in allowed_extensions):
        return False, "Please upload an Excel file (.xlsx or .xls)"
    
    if file.size > 16 * 1024 * 1024:  # 16MB limit
        return False, "File size must be less than 16MB"
    
    return True, "File is valid"

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
    """Get MIS data"""
    success, response = api_request('GET', '/mis-files')
    if success:
        return response.get('files', [])
    return []

def get_leads_data(status_filter=None):
    """Get leads data"""
    # For now, return empty list - implement when leads API is ready
    return []

def get_performance_data(days=30):
    """Get performance data"""
    # For now, return empty list - implement when performance API is ready
    return []

def get_team_members():
    """Get team members"""
    success, response = api_request('GET', '/users')
    if success:
        return response.get('users', [])
    return []

# User Management Functions
def get_user_role():
    """Get current user role"""
    user = st.session_state.get('user', {})
    return user.get('role', 'user')

def get_user_id():
    """Get current user ID"""
    user = st.session_state.get('user', {})
    return user.get('id')

def get_team_leader_id():
    """Get current user's team leader ID"""
    user = st.session_state.get('user', {})
    return user.get('team_leader_id')

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
    if not st.session_state.get('logged_in'):
        st.error("Please login to access this page")
        st.stop()

def require_role(required_role):
    """Require specific role to access page"""
    check_authentication()
    user_role = st.session_state.get('user', {}).get('role')
    
    if user_role != required_role:
        st.error(f"Access denied. {get_role_display_name(required_role)} role required.")
        st.stop()

def require_roles(allowed_roles):
    """Require one of the specified roles to access page"""
    check_authentication()
    user_role = st.session_state.get('user', {}).get('role')
    
    if user_role not in allowed_roles:
        role_names = [get_role_display_name(role) for role in allowed_roles]
        st.error(f"Access denied. One of these roles required: {', '.join(role_names)}")
        st.stop() 