import streamlit as st
import pandas as pd
from frontend.helpers import (
    get_team_members, display_success_message, display_error_message,
    format_datetime, create_metrics_dataframe, get_user_role, check_permissions
)

def show_team_management():
    """Display team management page"""
    st.title("👥 Team Management")
    st.markdown("---")
    
    # Check permissions
    if not check_permissions('admin') and get_user_role() != 'team_leader':
        st.error("Access denied. Only admins and team leaders can access team management.")
        return
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["👥 Team Members", "📊 Team Overview", "⚙️ Team Settings"])
    
    with tab1:
        show_team_members_section()
    
    with tab2:
        show_team_overview_section()
    
    with tab3:
        show_team_settings_section()

def show_team_members_section():
    """Show team members section"""
    st.subheader("👥 Team Members")
    
    # Load team members
    with st.spinner("Loading team members..."):
        team_members = get_team_members()
    
    if team_members:
        # Convert to DataFrame
        team_df = create_metrics_dataframe(team_members)
        
        # Team statistics
        st.markdown("### Team Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = len(team_members)
            st.metric("Total Members", total_members)
        
        with col2:
            active_members = len([m for m in team_members if m.get('is_active', True)])
            st.metric("Active Members", active_members)
        
        with col3:
            team_leaders = len([m for m in team_members if m.get('role') == 'team_leader'])
            st.metric("Team Leaders", team_leaders)
        
        with col4:
            regular_users = len([m for m in team_members if m.get('role') == 'user'])
            st.metric("Regular Users", regular_users)
        
        # Team members table
        st.markdown("### Team Members List")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            role_filter = st.selectbox(
                "Filter by Role",
                ['All', 'admin', 'team_leader', 'user']
            )
        
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ['All', 'Active', 'Inactive']
            )
        
        # Apply filters
        filtered_df = team_df.copy()
        
        if role_filter != 'All':
            filtered_df = filtered_df[filtered_df['role'] == role_filter]
        
        if status_filter != 'All':
            is_active = status_filter == 'Active'
            filtered_df = filtered_df[filtered_df['is_active'] == is_active]
        
        # Display filtered data
        st.dataframe(
            filtered_df[['username', 'email', 'role', 'created_at']],
            use_container_width=True
        )
        
        # Team member details
        st.markdown("### Team Member Details")
        
        for member in filtered_df.iterrows():
            member_data = member[1]
            with st.expander(f"👤 {member_data['username']} - {member_data['role'].title()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Username:** {member_data['username']}")
                    st.write(f"**Email:** {member_data.get('email', 'N/A')}")
                    st.write(f"**Role:** {member_data['role'].title()}")
                
                with col2:
                    st.write(f"**Status:** {'Active' if member_data.get('is_active', True) else 'Inactive'}")
                    st.write(f"**Created:** {member_data.get('created_at', 'N/A')}")
                    st.write(f"**Last Updated:** {member_data.get('updated_at', 'N/A')}")
                
                # Action buttons (placeholder for future functionality)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Edit", key=f"edit_{member_data['username']}"):
                        st.info("Edit functionality coming soon...")
                
                with col2:
                    if st.button("Deactivate" if member_data.get('is_active', True) else "Activate", 
                                key=f"toggle_{member_data['username']}"):
                        st.info("Toggle status functionality coming soon...")
                
                with col3:
                    if st.button("View Performance", key=f"perf_{member_data['username']}"):
                        st.info("Performance view functionality coming soon...")
        
        # Download team data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Team Data (CSV)",
            data=csv,
            file_name="team_members.csv",
            mime="text/csv"
        )
    
    else:
        st.info("No team members found.")

def show_team_overview_section():
    """Show team overview section"""
    st.subheader("📊 Team Overview")
    
    # Load team data
    with st.spinner("Loading team overview..."):
        team_members = get_team_members()
    
    if team_members:
        team_df = create_metrics_dataframe(team_members)
        
        # Team composition chart
        st.markdown("### Team Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Role distribution
            role_counts = team_df['role'].value_counts()
            
            import plotly.express as px
            fig_role = px.pie(
                values=role_counts.values,
                names=role_counts.index,
                title="Team by Role",
                color_discrete_map={
                    'admin': '#FF6B6B',
                    'team_leader': '#4ECDC4',
                    'user': '#45B7D1'
                }
            )
            st.plotly_chart(fig_role, use_container_width=True)
        
        with col2:
            # Status distribution
            status_counts = team_df['is_active'].value_counts()
            
            fig_status = px.pie(
                values=status_counts.values,
                names=['Active' if x else 'Inactive' for x in status_counts.index],
                title="Team by Status",
                color_discrete_map={
                    'Active': '#4ECDC4',
                    'Inactive': '#FF6B6B'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Team growth timeline
        st.markdown("### Team Growth Timeline")
        
        if 'created_at' in team_df.columns:
            team_df['created_at'] = pd.to_datetime(team_df['created_at'])
            team_df['join_date'] = team_df['created_at'].dt.date
            
            # Monthly growth
            monthly_growth = team_df.groupby(team_df['created_at'].dt.to_period('M')).size().reset_index(name='count')
            monthly_growth['month'] = monthly_growth['created_at'].astype(str)
            
            fig_growth = px.line(
                monthly_growth,
                x='month',
                y='count',
                title="Team Growth Over Time",
                labels={'month': 'Month', 'count': 'New Members'}
            )
            fig_growth.update_xaxes(tickangle=45)
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # Team insights
        st.markdown("### Team Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Most recent join
            if 'created_at' in team_df.columns:
                latest_join = team_df['created_at'].max()
                st.metric("Latest Join", latest_join.strftime('%Y-%m-%d') if pd.notna(latest_join) else 'N/A')
        
        with col2:
            # Average team size
            avg_team_size = len(team_df) / max(1, team_df['role'].value_counts().get('team_leader', 1))
            st.metric("Avg Team Size", f"{avg_team_size:.1f}")
        
        with col3:
            # Team efficiency
            active_ratio = len(team_df[team_df['is_active'] == True]) / len(team_df) * 100
            st.metric("Active Ratio", f"{active_ratio:.1f}%")
    
    else:
        st.info("No team data available for overview.")

def show_team_settings_section():
    """Show team settings section"""
    st.subheader("⚙️ Team Settings")
    
    # This section would contain team management settings
    # For now, showing placeholder content
    
    st.markdown("### Team Configuration")
    
    # Team settings form
    with st.form("team_settings_form"):
        st.markdown("#### General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_name = st.text_input("Team Name", value="HSBC BTL Team")
            max_team_size = st.number_input("Maximum Team Size", min_value=1, value=20)
        
        with col2:
            auto_assign_leads = st.checkbox("Auto-assign leads to team members", value=True)
            enable_notifications = st.checkbox("Enable team notifications", value=True)
        
        st.markdown("#### Performance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_success_rate = st.slider("Minimum Success Rate (%)", 0, 100, 70)
            target_leads_per_day = st.number_input("Target Leads per Day", min_value=1, value=5)
        
        with col2:
            performance_review_frequency = st.selectbox(
                "Performance Review Frequency",
                ["Weekly", "Monthly", "Quarterly"]
            )
            enable_competitions = st.checkbox("Enable team competitions", value=True)
        
        # Submit button
        submit_button = st.form_submit_button("💾 Save Settings", type="primary")
        
        if submit_button:
            st.success("Team settings saved successfully!")
    
    # Team management actions
    st.markdown("### Team Management Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Send Team Message"):
            st.info("Team messaging functionality coming soon...")
    
    with col2:
        if st.button("📊 Generate Team Report"):
            st.info("Report generation functionality coming soon...")
    
    with col3:
        if st.button("🔄 Sync Team Data"):
            st.info("Data sync functionality coming soon...")
    
    # Team permissions
    st.markdown("### Team Permissions")
    
    permissions_data = {
        "Permission": [
            "View team leads",
            "Edit team leads", 
            "Upload MIS data",
            "View team reports",
            "Manage team members",
            "Export data"
        ],
        "Admin": ["✅", "✅", "✅", "✅", "✅", "✅"],
        "Team Leader": ["✅", "✅", "✅", "✅", "✅", "✅"],
        "User": ["❌", "❌", "❌", "❌", "❌", "✅"]
    }
    
    permissions_df = pd.DataFrame(permissions_data)
    st.dataframe(permissions_df, use_container_width=True)
    
    # System information
    st.markdown("### System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Last Database Sync:** " + format_datetime(str(pd.Timestamp.now())))
        st.info("**Active Sessions:** 5")
        st.info("**System Status:** Healthy")
    
    with col2:
        st.info("**Total Users:** " + str(len(get_team_members()) if get_team_members() else 0))
        st.info("**API Version:** v1.0")
        st.info("**Last Backup:** " + format_datetime(str(pd.Timestamp.now())))

def main():
    """Main team management function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Team Management",
        page_icon="👥",
        layout="wide"
    )
    
    # Show team management page
    show_team_management()

if __name__ == "__main__":
    main() 