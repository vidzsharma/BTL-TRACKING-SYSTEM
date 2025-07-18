import streamlit as st
import pandas as pd
from frontend.helpers import (
    get_performance_data, get_leads_data, get_mis_data, get_team_members,
    display_success_message, display_error_message, format_datetime,
    create_metrics_dataframe, get_user_role, check_permissions
)

def show_reports():
    """Display reports page"""
    st.title("📋 Reports & Analytics")
    st.markdown("---")
    
    # Check permissions
    if not check_permissions('admin') and get_user_role() != 'team_leader':
        st.error("Access denied. Only admins and team leaders can access reports.")
        return
    
    # Create tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Reports", "📈 Lead Reports", "📁 MIS Reports", "📋 Custom Reports"])
    
    with tab1:
        show_performance_reports()
    
    with tab2:
        show_lead_reports()
    
    with tab3:
        show_mis_reports()
    
    with tab4:
        show_custom_reports()

def show_performance_reports():
    """Show performance reports"""
    st.subheader("📊 Performance Reports")
    
    # Load performance data
    with st.spinner("Loading performance data..."):
        performance_data = get_performance_data()
        team_members = get_team_members()
    
    if performance_data and team_members:
        perf_df = create_metrics_dataframe(performance_data)
        team_df = create_metrics_dataframe(team_members)
        
        # Report filters
        st.markdown("### Report Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Overall Performance", "Individual Performance", "Team Comparison", "Success Rate Analysis"]
            )
        
        with col2:
            date_range = st.selectbox(
                "Date Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "All time"]
            )
        
        with col3:
            export_format = st.selectbox(
                "Export Format",
                ["PDF", "Excel", "CSV"]
            )
        
        # Generate report based on type
        if report_type == "Overall Performance":
            show_overall_performance_report(perf_df, team_df)
        elif report_type == "Individual Performance":
            show_individual_performance_report(perf_df, team_df)
        elif report_type == "Team Comparison":
            show_team_comparison_report(perf_df, team_df)
        elif report_type == "Success Rate Analysis":
            show_success_rate_report(perf_df, team_df)
        
        # Export functionality
        st.markdown("### Export Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Report", type="primary"):
                st.info(f"Downloading {report_type} report in {export_format} format...")
        
        with col2:
            if st.button("📧 Email Report"):
                st.info("Email functionality coming soon...")
        
        with col3:
            if st.button("🖨️ Print Report"):
                st.info("Print functionality coming soon...")
    
    else:
        st.info("No performance data available for reports.")

def show_overall_performance_report(perf_df, team_df):
    """Show overall performance report"""
    st.markdown("### Overall Performance Report")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = perf_df['total_leads'].sum() if not perf_df.empty else 0
        st.metric("Total Leads", total_leads)
    
    with col2:
        closed_leads = perf_df['closed_leads'].sum() if not perf_df.empty else 0
        st.metric("Closed Leads", closed_leads)
    
    with col3:
        avg_success_rate = perf_df['success_rate'].mean() if not perf_df.empty else 0
        st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
    
    with col4:
        total_members = len(team_df) if not team_df.empty else 0
        st.metric("Team Size", total_members)
    
    # Performance visualization
    col1, col2 = st.columns(2)
    
    with col1:
        import plotly.express as px
        
        # Success rate distribution
        fig_success = px.histogram(
            perf_df,
            x='success_rate',
            title="Success Rate Distribution",
            labels={'success_rate': 'Success Rate (%)', 'count': 'Number of Members'},
            nbins=10
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    with col2:
        # Performance comparison
        fig_perf = px.bar(
            perf_df,
            x='username',
            y=['total_leads', 'closed_leads'],
            title="Performance Comparison",
            barmode='group'
        )
        fig_perf.update_xaxes(tickangle=45)
        st.plotly_chart(fig_perf, use_container_width=True)
    
    # Performance table
    st.markdown("### Performance Summary")
    
    if not perf_df.empty:
        summary_data = perf_df[['username', 'total_leads', 'closed_leads', 'in_progress_leads', 'success_rate']].copy()
        summary_data = summary_data.sort_values('success_rate', ascending=False)
        
        st.dataframe(summary_data, use_container_width=True)

def show_individual_performance_report(perf_df, team_df):
    """Show individual performance report"""
    st.markdown("### Individual Performance Report")
    
    # Member selection
    if not perf_df.empty:
        member_names = perf_df['username'].tolist()
        selected_member = st.selectbox("Select Team Member", member_names)
        
        if selected_member:
            member_data = perf_df[perf_df['username'] == selected_member].iloc[0]
            
            # Individual metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Leads", member_data['total_leads'])
            
            with col2:
                st.metric("Closed Leads", member_data['closed_leads'])
            
            with col3:
                st.metric("In Progress", member_data['in_progress_leads'])
            
            with col4:
                st.metric("Success Rate", f"{member_data['success_rate']}%")
            
            # Performance breakdown
            st.markdown("### Performance Breakdown")
            
            import plotly.express as px
            
            # Lead status pie chart
            status_data = {
                'Closed': member_data['closed_leads'],
                'In Progress': member_data['in_progress_leads'],
                'New': member_data['total_leads'] - member_data['closed_leads'] - member_data['in_progress_leads']
            }
            
            fig_pie = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title=f"{selected_member}'s Lead Status Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

def show_team_comparison_report(perf_df, team_df):
    """Show team comparison report"""
    st.markdown("### Team Comparison Report")
    
    if not perf_df.empty:
        # Team ranking
        st.markdown("### Team Ranking by Success Rate")
        
        ranking_data = perf_df[['username', 'success_rate', 'total_leads', 'closed_leads']].copy()
        ranking_data = ranking_data.sort_values('success_rate', ascending=False)
        ranking_data['Rank'] = range(1, len(ranking_data) + 1)
        
        st.dataframe(ranking_data, use_container_width=True)
        
        # Performance correlation
        st.markdown("### Performance Correlation Analysis")
        
        import plotly.express as px
        
        fig_corr = px.scatter(
            perf_df,
            x='total_leads',
            y='success_rate',
            title="Total Leads vs Success Rate",
            labels={'total_leads': 'Total Leads', 'success_rate': 'Success Rate (%)'},
            hover_data=['username']
        )
        st.plotly_chart(fig_corr, use_container_width=True)

def show_success_rate_report(perf_df, team_df):
    """Show success rate analysis report"""
    st.markdown("### Success Rate Analysis Report")
    
    if not perf_df.empty:
        # Success rate statistics
        st.markdown("### Success Rate Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_success = perf_df['success_rate'].mean()
            st.metric("Average Success Rate", f"{avg_success:.1f}%")
        
        with col2:
            max_success = perf_df['success_rate'].max()
            st.metric("Highest Success Rate", f"{max_success:.1f}%")
        
        with col3:
            min_success = perf_df['success_rate'].min()
            st.metric("Lowest Success Rate", f"{min_success:.1f}%")
        
        # Success rate distribution
        import plotly.express as px
        
        fig_dist = px.histogram(
            perf_df,
            x='success_rate',
            title="Success Rate Distribution",
            labels={'success_rate': 'Success Rate (%)', 'count': 'Number of Members'},
            nbins=10
        )
        st.plotly_chart(fig_dist, use_container_width=True)

def show_lead_reports():
    """Show lead reports"""
    st.subheader("📈 Lead Reports")
    
    # Load lead data
    with st.spinner("Loading lead data..."):
        leads_data = get_leads_data()
    
    if leads_data:
        leads_df = create_metrics_dataframe(leads_data)
        
        # Lead report filters
        st.markdown("### Report Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lead_report_type = st.selectbox(
                "Lead Report Type",
                ["Lead Status Report", "Campaign Performance", "Lead Timeline", "Lead Conversion"]
            )
        
        with col2:
            lead_date_range = st.selectbox(
                "Date Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
            )
        
        # Generate lead report
        if lead_report_type == "Lead Status Report":
            show_lead_status_report(leads_df)
        elif lead_report_type == "Campaign Performance":
            show_campaign_performance_report(leads_df)
        elif lead_report_type == "Lead Timeline":
            show_lead_timeline_report(leads_df)
        elif lead_report_type == "Lead Conversion":
            show_lead_conversion_report(leads_df)
    
    else:
        st.info("No lead data available for reports.")

def show_lead_status_report(leads_df):
    """Show lead status report"""
    st.markdown("### Lead Status Report")
    
    # Status summary
    status_counts = leads_df['lead_status'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(leads_df))
    
    with col2:
        st.metric("New Leads", status_counts.get('new', 0))
    
    with col3:
        st.metric("In Progress", status_counts.get('in-progress', 0))
    
    with col4:
        st.metric("Closed Leads", status_counts.get('closed', 0))
    
    # Status visualization
    import plotly.express as px
    
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Lead Status Distribution"
    )
    st.plotly_chart(fig_status, use_container_width=True)

def show_campaign_performance_report(leads_df):
    """Show campaign performance report"""
    st.markdown("### Campaign Performance Report")
    
    if 'campaign_tag' in leads_df.columns:
        # Campaign summary
        campaign_stats = leads_df.groupby('campaign_tag')['lead_status'].value_counts().unstack(fill_value=0)
        
        st.dataframe(campaign_stats, use_container_width=True)
        
        # Campaign visualization
        import plotly.express as px
        
        fig_campaign = px.bar(
            campaign_stats,
            title="Campaign Performance by Status",
            barmode='group'
        )
        fig_campaign.update_layout(height=400)
        st.plotly_chart(fig_campaign, use_container_width=True)

def show_lead_timeline_report(leads_df):
    """Show lead timeline report"""
    st.markdown("### Lead Timeline Report")
    
    if 'assigned_date' in leads_df.columns:
        # Timeline analysis
        leads_df['assigned_date'] = pd.to_datetime(leads_df['assigned_date'])
        leads_df['date'] = leads_df['assigned_date'].dt.date
        
        timeline_data = leads_df.groupby(['date', 'lead_status']).size().reset_index(name='count')
        
        import plotly.express as px
        
        fig_timeline = px.line(
            timeline_data,
            x='date',
            y='count',
            color='lead_status',
            title="Lead Creation Timeline",
            labels={'date': 'Date', 'count': 'Leads', 'lead_status': 'Status'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

def show_lead_conversion_report(leads_df):
    """Show lead conversion report"""
    st.markdown("### Lead Conversion Report")
    
    # Conversion metrics
    total_leads = len(leads_df)
    closed_leads = len(leads_df[leads_df['lead_status'] == 'closed'])
    conversion_rate = (closed_leads / total_leads * 100) if total_leads > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Leads", total_leads)
    
    with col2:
        st.metric("Converted Leads", closed_leads)
    
    with col3:
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")

def show_mis_reports():
    """Show MIS reports"""
    st.subheader("📁 MIS Reports")
    
    # Load MIS data
    with st.spinner("Loading MIS data..."):
        mis_data = get_mis_data()
    
    if mis_data:
        mis_df = create_metrics_dataframe(mis_data)
        
        # MIS report options
        st.markdown("### MIS Report Options")
        
        mis_report_type = st.selectbox(
            "MIS Report Type",
            ["Upload Summary", "Campaign Analysis", "Bank-wise Report", "Team Leader Report"]
        )
        
        if mis_report_type == "Upload Summary":
            show_mis_upload_summary(mis_df)
        elif mis_report_type == "Campaign Analysis":
            show_mis_campaign_analysis(mis_df)
        elif mis_report_type == "Bank-wise Report":
            show_mis_bank_report(mis_df)
        elif mis_report_type == "Team Leader Report":
            show_mis_team_leader_report(mis_df)
    
    else:
        st.info("No MIS data available for reports.")

def show_mis_upload_summary(mis_df):
    """Show MIS upload summary"""
    st.markdown("### MIS Upload Summary")
    
    # Upload statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(mis_df)
        st.metric("Total Records", total_records)
    
    with col2:
        unique_campaigns = mis_df['campaign_tag'].nunique()
        st.metric("Unique Campaigns", unique_campaigns)
    
    with col3:
        unique_banks = mis_df['bank'].nunique()
        st.metric("Unique Banks", unique_banks)
    
    with col4:
        unique_users = mis_df['username'].nunique()
        st.metric("Unique Users", unique_users)

def show_mis_campaign_analysis(mis_df):
    """Show MIS campaign analysis"""
    st.markdown("### MIS Campaign Analysis")
    
    # Campaign statistics
    campaign_stats = mis_df['campaign_tag'].value_counts()
    
    import plotly.express as px
    
    fig_campaign = px.bar(
        x=campaign_stats.index,
        y=campaign_stats.values,
        title="Records by Campaign",
        labels={'x': 'Campaign', 'y': 'Count'}
    )
    fig_campaign.update_xaxes(tickangle=45)
    st.plotly_chart(fig_campaign, use_container_width=True)

def show_mis_bank_report(mis_df):
    """Show MIS bank report"""
    st.markdown("### MIS Bank Report")
    
    # Bank statistics
    bank_stats = mis_df['bank'].value_counts()
    
    import plotly.express as px
    
    fig_bank = px.pie(
        values=bank_stats.values,
        names=bank_stats.index,
        title="Records by Bank"
    )
    st.plotly_chart(fig_bank, use_container_width=True)

def show_mis_team_leader_report(mis_df):
    """Show MIS team leader report"""
    st.markdown("### MIS Team Leader Report")
    
    if 'team_leader_name' in mis_df.columns:
        # Team leader statistics
        tl_stats = mis_df['team_leader_name'].value_counts()
        
        st.dataframe(tl_stats.reset_index().rename(
            columns={'index': 'Team Leader', 'team_leader_name': 'Records'}
        ), use_container_width=True)

def show_custom_reports():
    """Show custom reports"""
    st.subheader("📋 Custom Reports")
    
    st.markdown("### Create Custom Report")
    
    # Custom report builder
    with st.form("custom_report_form"):
        st.markdown("#### Report Configuration")
        
        # Data sources
        data_sources = st.multiselect(
            "Select Data Sources",
            ["Performance Data", "Lead Data", "MIS Data", "Team Data"]
        )
        
        # Metrics
        metrics = st.multiselect(
            "Select Metrics",
            ["Total Leads", "Closed Leads", "Success Rate", "Team Size", "Campaign Count"]
        )
        
        # Filters
        st.markdown("#### Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_from = st.date_input("From Date")
            status_filter = st.multiselect("Lead Status", ["new", "in-progress", "closed", "rejected"])
        
        with col2:
            date_to = st.date_input("To Date")
            campaign_filter = st.multiselect("Campaign Tags", ["All"])
        
        # Generate report
        if st.form_submit_button("🚀 Generate Custom Report", type="primary"):
            if data_sources and metrics:
                st.success("Custom report generated successfully!")
                
                # Placeholder for custom report display
                st.info("Custom report display functionality coming soon...")
            else:
                st.error("Please select at least one data source and metric.")
    
    # Saved reports
    st.markdown("### Saved Reports")
    
    saved_reports = [
        {"name": "Weekly Performance Report", "type": "Performance", "last_generated": "2024-01-15"},
        {"name": "Monthly Lead Summary", "type": "Lead", "last_generated": "2024-01-10"},
        {"name": "Campaign Analysis Q4", "type": "MIS", "last_generated": "2024-01-05"}
    ]
    
    for report in saved_reports:
        with st.expander(f"📄 {report['name']} ({report['type']})"):
            st.write(f"**Last Generated:** {report['last_generated']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Regenerate", key=f"regenerate_{report['name']}"):
                    st.info("Regenerating report...")
            
            with col2:
                if st.button("📥 Download", key=f"download_{report['name']}"):
                    st.info("Downloading report...")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{report['name']}"):
                    st.info("Deleting report...")

def main():
    """Main reports function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Reports",
        page_icon="📋",
        layout="wide"
    )
    
    # Show reports page
    show_reports()

if __name__ == "__main__":
    main() 