import streamlit as st
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

# Import frontend modules
from frontend.login import show_login_page
from frontend.dashboard import show_dashboard
from frontend.lead_management import show_lead_management
from frontend.team_progress import show_team_progress
from frontend.team_management import show_team_management
from frontend.reports import show_reports
from frontend.helpers import check_authentication, require_roles, get_role_display_name, get_user_role

def initialize_database():
    """Initialize the database with required tables"""
    try:
        from backend.db import init_db
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")

def start_backend_server():
    """Start the Flask backend server"""
    try:
        # Start the backend server
        backend_process = subprocess.Popen([
            sys.executable, "run_backend.py"
        ], cwd=os.getcwd())
        
        # Wait a moment for the server to start
        time.sleep(3)
        return backend_process
    except Exception as e:
        st.error(f"Failed to start backend server: {e}")
        return None

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="HSBC BTL Tracking Tool",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database on first run
    if 'db_initialized' not in st.session_state:
        initialize_database()
        st.session_state.db_initialized = True
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3c72;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .role-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Start backend server if not already running
    if 'backend_process' not in st.session_state:
        st.session_state.backend_process = start_backend_server()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏦 HSBC BTL Tracking Tool</h1>
        <p>Below the Line Credit Card Lead Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        if st.session_state.logged_in:
            # Display user info
            user = st.session_state.get('user', {})
            user_role = user.get('role', 'user')
            
            st.markdown(f"**Welcome, {user.get('username', 'User')}**")
            st.markdown(f"<div class='role-badge'>{get_role_display_name(user_role)}</div>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Navigation buttons with role-based access
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
            

            
            if st.button("🎯 Lead Management", use_container_width=True):
                st.session_state.current_page = 'leads'
            
            # Team Progress - Admin and Team Leaders only
            if user_role in ['admin', 'team_leader']:
                if st.button("👥 Team Progress", use_container_width=True):
                    st.session_state.current_page = 'team_progress'
            else:
                st.info("👥 Team Progress\n(Admin/Team Leader only)")
            
            # Team Management - Admin only
            if user_role == 'admin':
                if st.button("⚙️ Team Management", use_container_width=True):
                    st.session_state.current_page = 'team_management'
            else:
                st.info("⚙️ Team Management\n(Admin only)")
                
            if st.button("📈 Reports", use_container_width=True):
                    st.session_state.current_page = 'reports'
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Please login to access the system")
    
    # Main content area
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Check authentication
        if not check_authentication():
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.rerun()
        
        # Route to appropriate page
        current_page = st.session_state.current_page
        
        if current_page == 'dashboard':
            show_dashboard()
        elif current_page == 'leads':
            show_lead_management()
        elif current_page == 'team_progress':
            show_team_progress()
        elif current_page == 'team_management':
            show_team_management()
        elif current_page == 'reports':
            show_reports()
        else:
            show_dashboard()

if __name__ == "__main__":
        main()