import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.helpers import (
    get_dashboard_stats, get_mis_data, get_leads_data, 
    get_performance_data, format_datetime, display_error_message,
    get_user_role, get_team_members
)

def show_dashboard():
    """Display main dashboard"""
    st.title("📊 BTL Tracking Dashboard")
    st.markdown("---")
    
    # Get user role for conditional display
    user_role = get_user_role()
    
    # Load data
    with st.spinner("Loading dashboard data..."):
        stats = get_dashboard_stats()
        mis_data = get_mis_data()
        leads_data = get_leads_data()
        performance_data = get_performance_data()
        
        if user_role in ['admin', 'team_leader']:
            team_members = get_team_members()
    
    # Key Metrics Row
    st.subheader("📈 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = stats.get('total_leads', 0)
        st.metric(
            label="Total Leads",
            value=total_leads,
            delta=None
        )
    
    with col2:
        closed_leads = stats.get('status_breakdown', {}).get('closed', 0)
        st.metric(
            label="Closed Leads",
            value=closed_leads,
            delta=None
        )
    
    with col3:
        in_progress = stats.get('status_breakdown', {}).get('in-progress', 0)
        st.metric(
            label="In Progress",
            value=in_progress,
            delta=None
        )
    
    with col4:
        success_rate = 0
        if total_leads > 0:
            success_rate = round((closed_leads / total_leads) * 100, 1)
        st.metric(
            label="Success Rate",
            value=f"{success_rate}%",
            delta=None
        )
    
    # Charts Row
    st.markdown("---")
    st.subheader("📊 Analytics Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Lead Status Distribution
        if stats.get('status_breakdown'):
            status_data = stats['status_breakdown']
            fig_status = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Lead Status Distribution",
                color_discrete_map={
                    'new': '#FF6B6B',
                    'in-progress': '#4ECDC4',
                    'closed': '#45B7D1',
                    'rejected': '#96CEB4'
                }
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Performance Chart
        if performance_data:
            perf_df = pd.DataFrame(performance_data)
            if not perf_df.empty:
                fig_perf = px.bar(
                    perf_df,
                    x='username',
                    y=['total_leads', 'closed_leads', 'in_progress_leads'],
                    title="Team Performance",
                    barmode='group'
                )
                fig_perf.update_layout(height=400)
                st.plotly_chart(fig_perf, use_container_width=True)
    
    # Recent Activity
    st.markdown("---")
    st.subheader("🕒 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Recent Leads
        if leads_data:
            recent_leads = leads_data[:10]  # Show last 10 leads
            leads_df = pd.DataFrame(recent_leads)
            
            if not leads_df.empty:
                # Format datetime columns
                if 'assigned_date' in leads_df.columns:
                    leads_df['assigned_date'] = pd.to_datetime(leads_df['assigned_date'])
                    leads_df['assigned_date'] = leads_df['assigned_date'].dt.strftime('%Y-%m-%d %H:%M')
                
                st.markdown("**Recent Leads**")
                st.dataframe(
                    leads_df[['campaign_tag', 'lead_status', 'assigned_date', 'username']].head(5),
                    use_container_width=True
                )
    
    with col2:
        # Recent MIS Uploads
        if mis_data:
            recent_mis = mis_data[:10]  # Show last 10 uploads
            mis_df = pd.DataFrame(recent_mis)
            
            if not mis_df.empty:
                # Format datetime columns
                if 'uploaded_at' in mis_df.columns:
                    mis_df['uploaded_at'] = pd.to_datetime(mis_df['uploaded_at'])
                    mis_df['uploaded_at'] = mis_df['uploaded_at'].dt.strftime('%Y-%m-%d %H:%M')
                
                st.markdown("**Recent MIS Uploads**")
                st.dataframe(
                    mis_df[['campaign_tag', 'bank', 'uploaded_at', 'uploaded_by_username']].head(5),
                    use_container_width=True
                )
    
    # Team Overview (Admin/Team Leader only)
    if user_role in ['admin', 'team_leader']:
        st.markdown("---")
        st.subheader("👥 Team Overview")
        
        if team_members:
            team_df = pd.DataFrame(team_members)
            
            # Team member statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_members = len(team_members)
                st.metric("Total Team Members", total_members)
            
            with col2:
                active_members = len([m for m in team_members if m.get('is_active', True)])
                st.metric("Active Members", active_members)
            
            with col3:
                team_leaders = len([m for m in team_members if m.get('role') == 'team_leader'])
                st.metric("Team Leaders", team_leaders)
            
            # Team members table
            st.markdown("**Team Members**")
            st.dataframe(
                team_df[['username', 'email', 'role', 'created_at']],
                use_container_width=True
            )
    
    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Upload MIS", type="primary"):
            st.session_state.page = "mis"
            st.rerun()
    
    with col2:
        if st.button("🎯 Create Lead", type="primary"):
            st.session_state.page = "leads"
            st.rerun()
    
    with col3:
        if st.button("📈 View Reports", type="primary"):
            st.session_state.page = "reports"
            st.rerun()
    
    # System Status
    st.markdown("---")
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Database Connected")
    
    with col2:
        st.success("✅ API Running")
    
    with col3:
        st.success("✅ Authentication Active")
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard last updated: " + format_datetime(str(pd.Timestamp.now())) + "*")

def main():
    """Main dashboard function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show dashboard
    show_dashboard()

if __name__ == "__main__":
    main() 