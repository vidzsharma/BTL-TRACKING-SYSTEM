import streamlit as st
import pandas as pd
from frontend.helpers import (
    get_performance_data, get_team_members, get_leads_data,
    display_success_message, display_error_message, format_datetime,
    create_metrics_dataframe, get_user_role, get_mis_analytics,
    get_login_stats, get_lead_analytics, get_team_detailed_stats
)

def show_team_progress():
    """Display team progress page"""
    st.title("👥 Team Progress Tracking")
    st.markdown("---")
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Team Performance", 
        "👤 Individual Progress", 
        "📈 Progress Analytics",
        "📋 MIS Analytics",
        "🔐 Login Statistics"
    ])
    
    with tab1:
        show_team_performance_section()
    
    with tab2:
        show_individual_progress_section()
    
    with tab3:
        show_progress_analytics_section()
    
    with tab4:
        show_mis_analytics_section()
    
    with tab5:
        show_login_statistics_section()

def show_team_performance_section():
    """Show team performance section"""
    st.subheader("📊 Team Performance Overview")
    
    # Load performance data
    with st.spinner("Loading team performance data..."):
        performance_data = get_performance_data()
        team_members = get_team_members()
    
    if performance_data and team_members:
        # Convert to DataFrame
        perf_df = create_metrics_dataframe(performance_data)
        team_df = create_metrics_dataframe(team_members)
        
        # Team performance metrics
        st.markdown("### Team Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = len(team_members)
            st.metric("Total Team Members", total_members)
        
        with col2:
            total_leads = perf_df['total_leads'].sum() if not perf_df.empty else 0
            st.metric("Total Leads", total_leads)
        
        with col3:
            closed_leads = perf_df['closed_leads'].sum() if not perf_df.empty else 0
            st.metric("Closed Leads", closed_leads)
        
        with col4:
            avg_success_rate = 0
            if not perf_df.empty and perf_df['total_leads'].sum() > 0:
                avg_success_rate = round((closed_leads / total_leads) * 100, 1)
            st.metric("Average Success Rate", f"{avg_success_rate}%")
        
        # Performance chart
        st.markdown("### Team Performance Chart")
        
        if not perf_df.empty:
            import plotly.express as px
            
            # Create performance comparison chart
            fig_perf = px.bar(
                perf_df,
                x='username',
                y=['total_leads', 'closed_leads', 'in_progress_leads'],
                title="Team Performance Comparison",
                barmode='group',
                labels={'value': 'Count', 'variable': 'Lead Type'}
            )
            fig_perf.update_layout(height=500)
            st.plotly_chart(fig_perf, use_container_width=True)
        
        # Team members table with performance
        st.markdown("### Team Members Performance")
        
        if not perf_df.empty and not team_df.empty:
            # Merge team and performance data
            merged_df = team_df.merge(perf_df, on='username', how='left')
            
            # Display performance table
            display_columns = ['username', 'email', 'role', 'total_leads', 'closed_leads', 'in_progress_leads', 'success_rate']
            available_columns = [col for col in display_columns if col in merged_df.columns]
            
            st.dataframe(
                merged_df[available_columns].fillna(0),
                use_container_width=True
            )
        
        # Top performers
        st.markdown("### Top Performers")
        
        if not perf_df.empty:
            # Sort by success rate
            top_performers = perf_df.sort_values('success_rate', ascending=False).head(5)
            
            for idx, performer in top_performers.iterrows():
                with st.expander(f"🥇 {performer['username']} - Success Rate: {performer['success_rate']}%"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Leads", performer['total_leads'])
                    
                    with col2:
                        st.metric("Closed Leads", performer['closed_leads'])
                    
                    with col3:
                        st.metric("In Progress", performer['in_progress_leads'])
    
    else:
        st.info("No team performance data available.")

def show_individual_progress_section():
    """Show individual progress section"""
    st.subheader("👤 Individual Progress Tracking")
    
    # Load team members
    with st.spinner("Loading team members..."):
        team_members = get_team_members()
    
    if team_members:
        # Member selection
        member_names = [member['username'] for member in team_members]
        selected_member = st.selectbox("Select Team Member", member_names)
        
        if selected_member:
            # Load individual performance data
            with st.spinner(f"Loading {selected_member}'s progress..."):
                performance_data = get_performance_data()
                leads_data = get_leads_data()
            
            if performance_data:
                # Find selected member's performance
                member_perf = next((p for p in performance_data if p['username'] == selected_member), None)
                
                if member_perf:
                    st.markdown(f"### {selected_member}'s Performance")
                    
                    # Performance metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Leads", member_perf['total_leads'])
                    
                    with col2:
                        st.metric("Closed Leads", member_perf['closed_leads'])
                    
                    with col3:
                        st.metric("In Progress", member_perf['in_progress_leads'])
                    
                    with col4:
                        st.metric("Success Rate", f"{member_perf['success_rate']}%")
                    
                    # Performance visualization
                    st.markdown("### Performance Breakdown")
                    
                    import plotly.express as px
                    
                    # Create pie chart for lead status
                    status_data = {
                        'Closed': member_perf['closed_leads'],
                        'In Progress': member_perf['in_progress_leads'],
                        'New': member_perf['total_leads'] - member_perf['closed_leads'] - member_perf['in_progress_leads']
                    }
                    
                    fig_pie = px.pie(
                        values=list(status_data.values()),
                        names=list(status_data.keys()),
                        title=f"{selected_member}'s Lead Status Distribution",
                        color_discrete_map={
                            'Closed': '#45B7D1',
                            'In Progress': '#4ECDC4',
                            'New': '#FF6B6B'
                        }
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Recent activity
                    if leads_data:
                        st.markdown("### Recent Activity")
                        
                        # Filter leads for selected member
                        member_leads = [lead for lead in leads_data if lead.get('username') == selected_member]
                        
                        if member_leads:
                            leads_df = create_metrics_dataframe(member_leads[:10])  # Show last 10
                            
                            if not leads_df.empty:
                                st.dataframe(
                                    leads_df[['campaign_tag', 'lead_status', 'assigned_date', 'progress_notes']].head(5),
                                    use_container_width=True
                                )
                            else:
                                st.info("No recent leads found for this member.")
                        else:
                            st.info("No leads found for this member.")
                else:
                    st.warning(f"No performance data found for {selected_member}")
            else:
                st.info("No performance data available.")
    else:
        st.info("No team members available.")

def show_progress_analytics_section():
    """Show progress analytics section"""
    st.subheader("📈 Progress Analytics")
    
    # Load data for analytics
    with st.spinner("Loading progress analytics..."):
        performance_data = get_performance_data()
        leads_data = get_leads_data()
    
    if performance_data and leads_data:
        perf_df = create_metrics_dataframe(performance_data)
        leads_df = create_metrics_dataframe(leads_data)
        
        # Analytics overview
        st.markdown("### Progress Analytics Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate distribution
            st.markdown("**Success Rate Distribution**")
            
            if not perf_df.empty:
                import plotly.express as px
                
                fig_success = px.histogram(
                    perf_df,
                    x='success_rate',
                    title="Success Rate Distribution",
                    labels={'success_rate': 'Success Rate (%)', 'count': 'Number of Members'},
                    nbins=10
                )
                st.plotly_chart(fig_success, use_container_width=True)
        
        with col2:
            # Performance correlation
            st.markdown("**Performance Correlation**")
            
            if not perf_df.empty:
                fig_corr = px.scatter(
                    perf_df,
                    x='total_leads',
                    y='success_rate',
                    title="Total Leads vs Success Rate",
                    labels={'total_leads': 'Total Leads', 'success_rate': 'Success Rate (%)'},
                    hover_data=['username']
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # Detailed analytics
        st.markdown("### Detailed Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Performance Summary**")
            if not perf_df.empty:
                summary_stats = perf_df[['total_leads', 'closed_leads', 'in_progress_leads', 'success_rate']].describe()
                st.dataframe(summary_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Top Performers by Success Rate**")
            if not perf_df.empty:
                top_performers = perf_df.nlargest(5, 'success_rate')[['username', 'success_rate', 'total_leads']]
                st.dataframe(top_performers, use_container_width=True)
        
        # Timeline analysis
        if 'assigned_date' in leads_df.columns:
            st.markdown("### Progress Timeline Analysis")
            
            # Group by date and analyze progress
            leads_df['assigned_date'] = pd.to_datetime(leads_df['assigned_date'])
            leads_df['date'] = leads_df['assigned_date'].dt.date
            
            # Daily progress
            daily_progress = leads_df.groupby(['date', 'lead_status']).size().reset_index(name='count')
            
            import plotly.express as px
            fig_timeline = px.line(
                daily_progress,
                x='date',
                y='count',
                color='lead_status',
                title="Daily Lead Progress",
                labels={'date': 'Date', 'count': 'Leads', 'lead_status': 'Status'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Performance insights
        st.markdown("### Performance Insights")
        
        if not perf_df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_success_rate = perf_df['success_rate'].mean()
                st.metric("Average Success Rate", f"{avg_success_rate:.1f}%")
            
            with col2:
                best_performer = perf_df.loc[perf_df['success_rate'].idxmax()]
                st.metric("Best Performer", f"{best_performer['username']} ({best_performer['success_rate']:.1f}%)")
            
            with col3:
                total_team_leads = perf_df['total_leads'].sum()
                st.metric("Total Team Leads", total_team_leads)
        
        # Campaign performance
        if 'campaign_tag' in leads_df.columns:
            st.markdown("### Campaign Performance")
            
            campaign_stats = leads_df.groupby('campaign_tag')['lead_status'].value_counts().unstack(fill_value=0)
            
            if not campaign_stats.empty:
                fig_campaign = px.bar(
                    campaign_stats,
                    title="Campaign Performance by Status",
                    barmode='group'
                )
                fig_campaign.update_layout(height=400)
                st.plotly_chart(fig_campaign, use_container_width=True)
    
    else:
        st.info("No progress analytics data available.")

def show_mis_analytics_section():
    """Show comprehensive MIS analytics section"""
    st.subheader("📋 MIS Analytics Overview")
    
    # Load MIS analytics data
    with st.spinner("Loading MIS analytics..."):
        mis_analytics = get_mis_analytics()
        lead_analytics = get_lead_analytics()
        team_detailed_stats = get_team_detailed_stats()
    
    if mis_analytics:
        st.markdown("### MIS Data Summary")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = mis_analytics.get('total_records', 0)
            st.metric("Total Records", f"{total_records:,}")
        
        with col2:
            approved_apps = mis_analytics.get('approved_applications', 0)
            st.metric("Approved Applications", f"{approved_apps:,}")
        
        with col3:
            pending_apps = mis_analytics.get('pending_applications', 0)
            st.metric("Pending Applications", f"{pending_apps:,}")
        
        with col4:
            rejected_apps = mis_analytics.get('rejected_applications', 0)
            st.metric("Rejected Applications", f"{rejected_apps:,}")
        
        # Application status breakdown
        st.markdown("### Application Status Distribution")
        
        if approved_apps + pending_apps + rejected_apps > 0:
            import plotly.express as px
            
            status_data = {
                'Approved': approved_apps,
                'Pending': pending_apps,
                'Rejected': rejected_apps
            }
            
            fig_status = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Application Status Distribution",
                color_discrete_map={
                    'Approved': '#28a745',
                    'Pending': '#ffc107',
                    'Rejected': '#dc3545'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Card type analysis
        st.markdown("### Card Type Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            visa_platinum = mis_analytics.get('visa_platinum', 0)
            st.metric("VISA/Platinum Cards", f"{visa_platinum:,}")
        
        with col2:
            mastercard = mis_analytics.get('mastercard', 0)
            st.metric("Mastercard", f"{mastercard:,}")
        
        # Campaign and stage analysis
        st.markdown("### Campaign & Stage Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_campaigns = mis_analytics.get('unique_campaigns', 0)
            st.metric("Unique Campaigns", unique_campaigns)
        
        with col2:
            unique_drop_pages = mis_analytics.get('unique_drop_pages', 0)
            st.metric("Drop Pages", unique_drop_pages)
        
        with col3:
            unique_stages = mis_analytics.get('unique_stages', 0)
            st.metric("Lead Stages", unique_stages)
        
        # Average attempts
        avg_attempts = mis_analytics.get('avg_attempts', 0)
        if avg_attempts:
            st.metric("Average Attempts", f"{avg_attempts:.1f}")
    
    # Lead Analytics by Status
    if lead_analytics:
        st.markdown("### Lead Analytics by Status")
        
        # Convert to DataFrame for better visualization
        lead_df = pd.DataFrame(lead_analytics)
        
        if not lead_df.empty:
            # Filter top results for display
            top_analytics = lead_df.head(10)
            
            # Display key analytics
            st.markdown("**Top Lead Analytics**")
            st.dataframe(
                top_analytics[['application_status', 'customer_dropped_page', 'lead_generation_stage', 'card_type', 'status', 'count']],
                use_container_width=True
            )
            
            # Application status breakdown
            if 'application_status' in lead_df.columns:
                st.markdown("**Application Status Breakdown**")
                status_counts = lead_df.groupby('application_status')['count'].sum().reset_index()
                
                fig_status_breakdown = px.bar(
                    status_counts,
                    x='application_status',
                    y='count',
                    title="Application Status Breakdown",
                    color='application_status'
                )
                st.plotly_chart(fig_status_breakdown, use_container_width=True)
            
            # Card type breakdown
            if 'card_type' in lead_df.columns:
                st.markdown("**Card Type Breakdown**")
                card_counts = lead_df.groupby('card_type')['count'].sum().reset_index()
                
                fig_card_breakdown = px.bar(
                    card_counts,
                    x='card_type',
                    y='count',
                    title="Card Type Distribution",
                    color='card_type'
                )
                st.plotly_chart(fig_card_breakdown, use_container_width=True)
    
    # Team Member Detailed Stats
    if team_detailed_stats:
        st.markdown("### Team Member Detailed Statistics")
        
        team_df = pd.DataFrame(team_detailed_stats)
        
        if not team_df.empty:
            # Key performance metrics
            st.markdown("**Team Member Performance Overview**")
            
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
            st.markdown("**Team Member Performance Comparison**")
            
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
        st.info("No MIS analytics data available.")

def show_login_statistics_section():
    """Show user login statistics including location and time"""
    st.subheader("🔐 Login Statistics")
    
    # Load login statistics
    with st.spinner("Loading login statistics..."):
        login_stats = get_login_stats()
    
    if login_stats:
        st.markdown("### User Login Activity")
        
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
            
            # Login patterns
            st.markdown("### Login Patterns")
            
            if 'last_login' in login_df.columns:
                # Group by hour to see login time patterns
                login_df['login_hour'] = login_df['last_login'].dt.hour
                hour_counts = login_df['login_hour'].value_counts().sort_index().reset_index()
                hour_counts.columns = ['hour', 'count']
                
                fig_hour_pattern = px.line(
                    hour_counts,
                    x='hour',
                    y='count',
                    title="Login Activity by Hour of Day",
                    markers=True
                )
                fig_hour_pattern.update_xaxes(range=[0, 23])
                st.plotly_chart(fig_hour_pattern, use_container_width=True)
    
    else:
        st.info("No login statistics data available.")

def main():
    """Main team progress function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Team Progress",
        page_icon="👥",
        layout="wide"
    )
    
    # Show team progress page
    show_team_progress()

if __name__ == "__main__":
    main() 