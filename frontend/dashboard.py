import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.helpers import (
    get_dashboard_stats, get_mis_data, get_leads_data, 
    get_performance_data, format_datetime, display_error_message,
    get_user_role, get_team_members, get_current_user,
    get_mis_analytics, get_login_stats, get_lead_analytics,
    get_team_detailed_stats
)

def show_dashboard():
    """Display main dashboard with role-based access control"""
    st.title("📊 BTL Tracking Dashboard")
    st.markdown("---")
    
    # Get user role and current user info for conditional display
    user_role = get_user_role()
    current_user = get_current_user()
    
    # Load data based on role hierarchy
    with st.spinner("Loading dashboard data..."):
        stats = get_dashboard_stats()
        mis_data = get_mis_data()
        leads_data = get_leads_data()
        
        # Only load analytics data for team leaders and admins
        performance_data = None
        mis_analytics = None
        login_stats = None
        lead_analytics = None
        team_detailed_stats = None
        
        if user_role in ['admin', 'team_leader']:
            performance_data = get_performance_data()
            mis_analytics = get_mis_analytics()
            login_stats = get_login_stats()
            lead_analytics = get_lead_analytics()
            
            # Load team detailed stats for Team Leaders
            if user_role == 'team_leader':
                team_detailed_stats = get_team_detailed_stats()
        
        if user_role in ['admin', 'team_leader']:
            team_members = get_team_members()
    
    # Team Member Filter (for Team Leaders)
    selected_team_member = None
    if user_role == 'team_leader' and team_members:
        st.subheader("👥 Team Member Filter")
        team_member_options = ['All Team Members'] + [member['username'] for member in team_members]
        selected_team_member = st.selectbox(
            "Select team member to view their data:",
            team_member_options,
            index=0
        )
        
        # Filter data based on selected team member
        if selected_team_member != 'All Team Members':
            # Update data to show only selected team member's data
            stats = get_dashboard_stats(team_member=selected_team_member)
            leads_data = get_leads_data(team_member=selected_team_member)
            performance_data = get_performance_data(team_member=selected_team_member)
    
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
        closed_leads = stats.get('closed_leads', 0)
        st.metric(
            label="Closed Leads",
            value=closed_leads,
            delta=None
        )
    
    with col3:
        in_progress = stats.get('in_progress_leads', 0)
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
    
    # MIS Data Section - Show full MIS data for users
    if mis_data:
        st.markdown("---")
        st.subheader("📋 My MIS Data")
        
        # Convert to DataFrame for better display
        mis_df = pd.DataFrame(mis_data)
        
        if not mis_df.empty:
            st.markdown(f"**Total MIS Records: {len(mis_df)}**")
            
            # Show MIS Statistics for users
            st.markdown("### 📊 MIS Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Application Status breakdown
                if 'application_status' in mis_df.columns:
                    status_counts = mis_df['application_status'].value_counts()
                    total_status = len(mis_df)
                    st.metric("Total Applications", total_status)
                else:
                    st.metric("Total Applications", len(mis_df))
            
            with col2:
                # Customer Dropped Page analysis
                if 'customer_dropped_page' in mis_df.columns:
                    drop_page_counts = mis_df['customer_dropped_page'].value_counts()
                    if not drop_page_counts.empty:
                        most_dropped = drop_page_counts.index[0]
                        st.metric("Most Dropped Page", most_dropped)
                    else:
                        st.metric("Most Dropped Page", "N/A")
                else:
                    st.metric("Most Dropped Page", "N/A")
            
            with col3:
                # Card Type analysis
                if 'card_type' in mis_df.columns:
                    card_counts = mis_df['card_type'].value_counts()
                    if not card_counts.empty:
                        most_card = card_counts.index[0]
                        st.metric("Most Card Type", most_card)
                    else:
                        st.metric("Most Card Type", "N/A")
                else:
                    st.metric("Most Card Type", "N/A")
            
            with col4:
                # Lead Generation Stage
                if 'lead_generation_stage' in mis_df.columns:
                    stage_counts = mis_df['lead_generation_stage'].value_counts()
                    if not stage_counts.empty:
                        most_stage = stage_counts.index[0]
                        st.metric("Most Stage", most_stage)
                    else:
                        st.metric("Most Stage", "N/A")
                else:
                    st.metric("Most Stage", "N/A")
            
            # Detailed Statistics
            st.markdown("### 📈 Detailed Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Application Status Chart
                if 'application_status' in mis_df.columns:
                    status_counts = mis_df['application_status'].value_counts()
                    if not status_counts.empty:
                        fig_status = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Application Status Distribution"
                        )
                        st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # Customer Dropped Page Chart
                if 'customer_dropped_page' in mis_df.columns:
                    drop_counts = mis_df['customer_dropped_page'].value_counts().head(10)
                    if not drop_counts.empty:
                        fig_drop = px.bar(
                            x=drop_counts.index,
                            y=drop_counts.values,
                            title="Top 10 Customer Drop Pages",
                            labels={'x': 'Drop Page', 'y': 'Count'}
                        )
                        st.plotly_chart(fig_drop, use_container_width=True)
            
            # Show all MIS data in a table
            st.markdown("### 📋 Complete MIS Data")
            st.dataframe(
                mis_df,
                use_container_width=True,
                height=400
            )
            
            # Add download button for the data
            csv = mis_df.to_csv(index=False)
            st.download_button(
                label="📥 Download MIS Data as CSV",
                data=csv,
                file_name=f"mis_data_{current_user.get('username', 'user')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No MIS data available.")
    else:
        st.info("No MIS data available.")
    
    # Charts Row (only for team leaders and admins)
    if user_role in ['admin', 'team_leader']:
        st.markdown("---")
        st.subheader("📊 Performance Charts")
        
        # Lead Performance Chart
        if performance_data:
            show_lead_performance_charts(performance_data, leads_data)
        else:
            st.info("No performance data available.")
        
        # Campaign Analysis Chart
        if leads_data:
            show_campaign_analysis_charts(leads_data)
        else:
            st.info("No leads data available.")
        
        # MIS Analytics Section
        if mis_analytics or lead_analytics:
            st.markdown("---")
            show_mis_analytics_charts(mis_analytics, lead_analytics, team_detailed_stats, user_role)
        
        # Login Statistics Section (only for team leaders and admins)
        if login_stats:
            st.markdown("---")
            show_login_statistics_section(login_stats)
        
        # Team Analytics Section (for Team Leaders and Admins)
        if team_detailed_stats and user_role in ['admin', 'team_leader']:
            st.markdown("---")
            show_team_analytics_section(team_detailed_stats, user_role)
    
    # Recent Activity Section
    st.markdown("---")
    st.subheader("🕒 Recent Activity")
    
    # Show recent leads
    if leads_data:
        recent_leads = leads_data[:10]  # Show last 10 leads
        if recent_leads:
            st.markdown("### Recent Leads")
            leads_df = pd.DataFrame(recent_leads)
            
            # Format datetime columns
            if 'created_at' in leads_df.columns:
                leads_df['created_at'] = pd.to_datetime(leads_df['created_at'])
                leads_df['created_at'] = leads_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Select columns to display
            display_columns = ['lead_id', 'status', 'campaign_tag', 'created_at']
            available_columns = [col for col in display_columns if col in leads_df.columns]
            
            st.dataframe(
                leads_df[available_columns],
                use_container_width=True
            )
        else:
            st.info("No recent leads found.")
    else:
        st.info("No leads data available.")

def show_lead_performance_charts(performance_data, leads_data):
    """Show lead performance charts."""
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        if not perf_df.empty and len(perf_df) > 0:
            # Ensure required columns exist
            required_cols = ['username', 'total_leads', 'closed_leads', 'in_progress_leads']
            if all(col in perf_df.columns for col in required_cols):
                fig_perf = px.bar(
                    perf_df,
                    x='username',
                    y=['total_leads', 'closed_leads', 'in_progress_leads'],
                    title="Team Performance",
                    barmode='group'
                )
                fig_perf.update_layout(height=400)
                st.plotly_chart(fig_perf, use_container_width=True)
            else:
                st.info("Performance data format not available.")
        else:
            st.info("No performance data available for the selected scope.")
    else:
        st.info("No performance data available.")

def show_campaign_analysis_charts(leads_data):
    """Show campaign analysis charts."""
    if leads_data:
        # Group leads by campaign_tag
        campaign_data = {}
        for lead in leads_data:
            campaign_tag = lead.get('campaign_tag')
            if campaign_tag:
                campaign_data.setdefault(campaign_tag, []).append(lead)

        # Convert list of leads to a DataFrame for plotting
        campaign_df = pd.DataFrame([
            {
                'campaign_tag': k,
                'total_leads': len(v),
                'closed_leads': sum(1 for l in v if l.get('status') == 'closed'),
                'in_progress_leads': sum(1 for l in v if l.get('status') == 'in-progress')
            }
            for k, v in campaign_data.items()
        ])

        if not campaign_df.empty and len(campaign_df) > 0:
            # Ensure required columns exist
            required_cols = ['campaign_tag', 'total_leads', 'closed_leads', 'in_progress_leads']
            if all(col in campaign_df.columns for col in required_cols):
                fig_campaign = px.bar(
                    campaign_df,
                    x='campaign_tag',
                    y=['total_leads', 'closed_leads', 'in_progress_leads'],
                    title="Leads by Campaign",
                    barmode='group'
                )
                fig_campaign.update_layout(height=400)
                st.plotly_chart(fig_campaign, use_container_width=True)
            else:
                st.info("Campaign data format not available.")
        else:
            st.info("No campaign data available for the selected scope.")
    else:
        st.info("No campaign data available.")

def show_mis_analytics_charts(mis_analytics, lead_analytics, team_detailed_stats, user_role):
    """Show MIS analytics charts"""
    if mis_analytics:
        st.markdown("### MIS Data Overview")
    
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            total_records = mis_analytics.get('total_records', 0) or 0
            st.metric("Total Records", f"{total_records:,}")
        
        with col2:
            approved_apps = mis_analytics.get('approved_applications', 0) or 0
            st.metric("Approved", f"{approved_apps:,}")
        
        with col3:
            pending_apps = mis_analytics.get('pending_applications', 0) or 0
            st.metric("Pending", f"{pending_apps:,}")
        
        with col4:
            rejected_apps = mis_analytics.get('rejected_applications', 0) or 0
            st.metric("Rejected", f"{rejected_apps:,}")
        
        # Application status pie chart
        if approved_apps + pending_apps + rejected_apps > 0:
            status_data = {
                'Approved': approved_apps,
                'Pending': pending_apps,
                'Rejected': rejected_apps
            }
            
            fig_status = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Application Status Distribution"
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)

def show_login_statistics_section(login_stats):
    """Show user login statistics including location and time"""
    st.markdown("### User Login Activity")
        
    if login_stats:
        # Convert to DataFrame
        login_df = pd.DataFrame(login_stats)
        
        if not login_df.empty:
            # Overall statistics
            st.markdown("### Overall Login Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_users = len(login_df)
                st.metric("Active Users", total_users)
            
            with col2:
                total_logins = login_df['total_logins'].sum() if 'total_logins' in login_df.columns else 0
                st.metric("Total Logins", f"{total_logins:,}")
            
            with col3:
                avg_logins = total_logins / total_users if total_users > 0 else 0
                st.metric("Avg Logins per User", f"{avg_logins:.1f}")
            
            # Login activity table
            st.markdown("### Detailed Login Statistics")
            
            # Format datetime columns
            if 'last_login' in login_df.columns:
                login_df['last_login'] = pd.to_datetime(login_df['last_login'])
                login_df['last_login_formatted'] = login_df['last_login'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Select columns to display
            display_columns = ['username', 'total_logins', 'last_login_formatted', 'location', 'ip_address']
            available_columns = [col for col in display_columns if col in login_df.columns]
            
            st.dataframe(
                login_df[available_columns].fillna('N/A'),
                use_container_width=True
            )
    
            # Login activity visualization
            st.markdown("### Login Activity Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Login frequency by user
                if 'total_logins' in login_df.columns and 'username' in login_df.columns:
                    fig_login_freq = px.bar(
                        login_df,
                        x='username',
                        y='total_logins',
                        title="Login Frequency by User",
                        color='total_logins'
                    )
                    st.plotly_chart(fig_login_freq, use_container_width=True)

            with col2:
                # Location distribution
                if 'location' in login_df.columns:
                    location_counts = login_df['location'].value_counts().reset_index()
                    location_counts.columns = ['location', 'count']
                    
                    fig_location = px.pie(
                        location_counts,
                        values='count',
                        names='location',
                        title="Login Location Distribution"
                    )
                    st.plotly_chart(fig_location, use_container_width=True)
            
            # Recent login activity
            st.markdown("### Recent Login Activity")
            
            if 'last_login' in login_df.columns:
                # Filter recent logins (last 7 days)
                recent_logins = login_df[login_df['last_login'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
                
                if not recent_logins.empty:
                    st.markdown("**Users who logged in within the last 7 days:**")
                    
                    recent_display = recent_logins[['username', 'last_login_formatted', 'location']].copy()
                    st.dataframe(recent_display, use_container_width=True)
                else:
                    st.info("No recent login activity in the last 7 days.")
    
    else:
        st.info("No login statistics data available.")

def show_team_analytics_section(team_detailed_stats, user_role):
    """Show team analytics for team leaders"""
    st.markdown("### Team Member Analytics")
    
    if team_detailed_stats and user_role in ['admin', 'team_leader']:
        team_df = pd.DataFrame(team_detailed_stats)
        
        if not team_df.empty:
            # Key performance metrics
            st.markdown("### Team Member Performance Overview")
            
            # Select columns to display
            display_columns = [
                'username', 'total_leads', 'closed_leads', 'in_progress_leads',
                'total_mis_records', 'approved_applications', 'pending_applications',
                'total_logins', 'last_login'
            ]
            
            available_columns = [col for col in display_columns if col in team_df.columns]
            
            st.dataframe(
                team_df[available_columns].fillna(0),
                use_container_width=True
            )
            
            # Performance visualization
            st.markdown("### Team Member Performance Comparison")
            
            if 'total_leads' in team_df.columns and 'username' in team_df.columns:
                fig_team_perf = px.bar(
                    team_df,
                    x='username',
                    y=['total_leads', 'closed_leads', 'in_progress_leads'],
                    title="Team Member Lead Performance",
                    barmode='group'
                )
                st.plotly_chart(fig_team_perf, use_container_width=True)
    
            # MIS Records comparison
            if 'total_mis_records' in team_df.columns and 'username' in team_df.columns:
                fig_mis_perf = px.bar(
                    team_df,
                    x='username',
                    y=['total_mis_records', 'approved_applications', 'pending_applications'],
                    title="Team Member MIS Performance",
                    barmode='group'
                )
                st.plotly_chart(fig_mis_perf, use_container_width=True)
    
    else:
        st.info("No team analytics data available.")

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