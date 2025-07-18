import streamlit as st
import pandas as pd
from frontend.helpers import (
    get_performance_data, get_team_members, get_leads_data,
    display_success_message, display_error_message, format_datetime,
    create_metrics_dataframe, get_user_role
)

def show_team_progress():
    """Display team progress page"""
    st.title("👥 Team Progress Tracking")
    st.markdown("---")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📊 Team Performance", "👤 Individual Progress", "📈 Progress Analytics"])
    
    with tab1:
        show_team_performance_section()
    
    with tab2:
        show_individual_progress_section()
    
    with tab3:
        show_progress_analytics_section()

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