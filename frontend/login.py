import streamlit as st
from frontend.helpers import login_user, display_error_message, display_success_message

def show_login_page():
    """Display login page"""
    st.title("🔐 BTL Tracking Tool - Login")
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to HSBC BTL Tracking System")
        st.markdown("Please enter your credentials to access the system.")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            # Login button
            submit_button = st.form_submit_button("Login", type="primary")
            
            if submit_button:
                if username and password:
                    with st.spinner("Logging in..."):
                        success, message = login_user(username, password)
                        if success:
                            display_success_message(message)
                            st.rerun()
                        else:
                            display_error_message(message)
                else:
                    display_error_message("Please enter both username and password")
        
        # Demo credentials
        st.markdown("---")
        st.markdown("### Demo Credentials")
        st.markdown("**Admin User:**")
        st.code("Username: admin\nPassword: admin123")
        
        st.markdown("**Note:** This is a demo system. In production, use your actual HSBC credentials.")
        
        # Additional information
        st.markdown("---")
        st.markdown("### System Features")
        st.markdown("""
        - **User Authentication** with role-based access
        - **MIS Data Management** for campaign tracking
        - **Lead Progress Tracking** with real-time updates
        - **Team Performance Analytics** and reporting
        - **Location-based Login Tracking** for field workers
        """)
        
        # Footer
        st.markdown("---")
        st.markdown("*HSBC Bank - Below the Line Tracking Tool*")
        st.markdown("*Version 1.0*")

def main():
    """Main login function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Login",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .login-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .demo-credentials {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show login page
    show_login_page()

if __name__ == "__main__":
    main() 