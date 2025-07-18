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
from frontend.upload_mis import show_mis_upload
from frontend.lead_management import show_lead_management
from frontend.team_progress import show_team_progress
from frontend.team_management import show_team_management
from frontend.reports import show_reports
from frontend.helpers import check_authentication, require_roles, get_role_display_name

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
            st.markdown(f"**Welcome, {user.get('username', 'User')}**")
            st.markdown(f"*{get_role_display_name(user.get('role', 'user'))}*")
            st.markdown("---")
            
            # Navigation buttons
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
            
            if st.button("📁 MIS Upload", use_container_width=True):
                st.session_state.current_page = 'mis_upload'
            
            if st.button("🎯 Lead Management", use_container_width=True):
                st.session_state.current_page = 'lead_management'
            
            if st.button("📈 Team Progress", use_container_width=True):
                st.session_state.current_page = 'team_progress'
            
            # Admin/Team Leader only pages
            user_role = user.get('role', 'user')
            if user_role in ['admin', 'team_leader']:
                if st.button("👥 Team Management", use_container_width=True):
                    st.session_state.current_page = 'team_management'
                
                if st.button("📋 Reports", use_container_width=True):
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
        # Route to appropriate page based on current_page
        current_page = st.session_state.current_page
        
        if current_page == 'dashboard':
            show_dashboard()
        elif current_page == 'mis_upload':
            show_mis_upload()
        elif current_page == 'lead_management':
            show_lead_management()
        elif current_page == 'team_progress':
            show_team_progress()
        elif current_page == 'team_management':
            require_roles(['admin', 'team_leader'])
            show_team_management()
        elif current_page == 'reports':
            require_roles(['admin', 'team_leader'])
            show_reports()
        else:
            show_dashboard()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Clean up backend process on exit
        if 'backend_process' in st.session_state and st.session_state.backend_process:
            st.session_state.backend_process.terminate()
    except Exception as e:
        st.error(f"Application error: {e}")
        # Clean up backend process on error
        if 'backend_process' in st.session_state and st.session_state.backend_process:
            st.session_state.backend_process.terminate() 