import streamlit as st
import pandas as pd
from frontend.helpers import (
    get_leads_data, create_lead, update_lead_progress, get_lead_details,
    get_lead_status_options, display_success_message, display_error_message,
    format_datetime, create_metrics_dataframe, get_user_role
)

def show_lead_management():
    """Display lead management page"""
    st.title("🎯 Lead Management")
    st.markdown("---")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📝 Create Lead", "📊 View Leads", "📈 Lead Analytics"])
    
    with tab1:
        show_create_lead_section()
    
    with tab2:
        show_view_leads_section()
    
    with tab3:
        show_lead_analytics_section()

def show_create_lead_section():
    """Show lead creation section"""
    st.subheader("📝 Create New Lead")
    st.markdown("Create a new lead with campaign information.")
    
    # Lead creation form
    with st.form("create_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_tag = st.text_input("Campaign Tag *", placeholder="e.g., CAMP001")
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            customer_phone = st.text_input("Customer Phone", placeholder="Enter phone number")
        
        with col2:
            customer_email = st.text_input("Customer Email", placeholder="Enter email address")
            bank_name = st.text_input("Bank Name", placeholder="e.g., HSBC")
            progress_notes = st.text_area("Initial Notes", placeholder="Enter any initial notes")
        
        # Submit button
        submit_button = st.form_submit_button("🚀 Create Lead", type="primary")
        
        if submit_button:
            if not campaign_tag:
                display_error_message("Campaign tag is required!")
            else:
                # Prepare lead data
                lead_data = {
                    "campaign_tag": campaign_tag,
                    "customer_name": customer_name or None,
                    "customer_phone": customer_phone or None,
                    "customer_email": customer_email or None,
                    "bank_name": bank_name or None
                }
                
                # Create lead
                success, result = create_lead(lead_data)
                
                if success:
                    display_success_message("Lead created successfully!")
                    st.info(f"Lead ID: {result.get('lead_id', 'N/A')}")
                else:
                    display_error_message(f"Failed to create lead: {result}")

def show_view_leads_section():
    """Show leads viewing section"""
    st.subheader("📊 View Leads")
    
    # Load leads data
    with st.spinner("Loading leads data..."):
        leads_data = get_leads_data()
    
    if leads_data:
        # Convert to DataFrame
        df = create_metrics_dataframe(leads_data)
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Status filter
            status_options = ['All'] + get_lead_status_options()
            selected_status = st.selectbox("Lead Status", status_options)
        
        with col2:
            # Campaign filter
            campaigns = ['All'] + sorted(df['campaign_tag'].unique().tolist())
            selected_campaign = st.selectbox("Campaign", campaigns)
        
        with col3:
            # Date range filter
            if 'assigned_date' in df.columns:
                df['assigned_date'] = pd.to_datetime(df['assigned_date'])
                min_date = df['assigned_date'].min()
                max_date = df['assigned_date'].max()
                
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['lead_status'] == selected_status]
        
        if selected_campaign != 'All':
            filtered_df = filtered_df[filtered_df['campaign_tag'] == selected_campaign]
        
        if 'assigned_date' in filtered_df.columns and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['assigned_date'].dt.date >= start_date) &
                (filtered_df['assigned_date'].dt.date <= end_date)
            ]
        
        # Display filtered data
        st.markdown(f"### Leads ({len(filtered_df)} records)")
        
        # Show key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_leads = len(filtered_df)
            st.metric("Total Leads", total_leads)
        
        with col2:
            new_leads = len(filtered_df[filtered_df['lead_status'] == 'new'])
            st.metric("New Leads", new_leads)
        
        with col3:
            in_progress = len(filtered_df[filtered_df['lead_status'] == 'in-progress'])
            st.metric("In Progress", in_progress)
        
        with col4:
            closed_leads = len(filtered_df[filtered_df['lead_status'] == 'closed'])
            st.metric("Closed Leads", closed_leads)
        
        # Data table with action buttons
        st.markdown("### Lead Details")
        
        # Display leads in a more interactive way
        for index, lead in filtered_df.iterrows():
            with st.expander(f"Lead #{lead.get('lead_id', index)} - {lead.get('campaign_tag', 'N/A')} ({lead.get('lead_status', 'N/A')})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Customer:** {lead.get('customer_name', 'N/A')}")
                    st.write(f"**Phone:** {lead.get('customer_phone', 'N/A')}")
                    st.write(f"**Email:** {lead.get('customer_email', 'N/A')}")
                    st.write(f"**Bank:** {lead.get('bank_name', 'N/A')}")
                    st.write(f"**Assigned Date:** {lead.get('assigned_date', 'N/A')}")
                    st.write(f"**Notes:** {lead.get('progress_notes', 'N/A')}")
                
                with col2:
                    # Update progress form
                    with st.form(f"update_lead_{lead.get('lead_id', index)}"):
                        new_status = st.selectbox(
                            "Status",
                            get_lead_status_options(),
                            index=get_lead_status_options().index(lead.get('lead_status', 'new')),
                            key=f"status_{lead.get('lead_id', index)}"
                        )
                        
                        progress_notes = st.text_area(
                            "Progress Notes",
                            value=lead.get('progress_notes', ''),
                            key=f"notes_{lead.get('lead_id', index)}"
                        )
                        
                        if st.form_submit_button("Update"):
                            progress_data = {
                                "progress_status": new_status,
                                "progress_notes": progress_notes
                            }
                            
                            success, message = update_lead_progress(
                                lead.get('lead_id'), progress_data
                            )
                            
                            if success:
                                display_success_message("Lead updated successfully!")
                                st.rerun()
                            else:
                                display_error_message(f"Failed to update lead: {message}")
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Leads Data (CSV)",
            data=csv,
            file_name=f"leads_{selected_campaign}_{selected_status}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("No leads available. Create some leads first!")

def show_lead_analytics_section():
    """Show lead analytics section"""
    st.subheader("📈 Lead Analytics")
    
    # Load leads data for analytics
    with st.spinner("Loading lead analytics..."):
        leads_data = get_leads_data()
    
    if leads_data:
        df = create_metrics_dataframe(leads_data)
        
        # Analytics overview
        st.markdown("### Overview Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Lead status distribution
            st.markdown("**Lead Status Distribution**")
            status_counts = df['lead_status'].value_counts()
            
            import plotly.express as px
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Leads by Status",
                color_discrete_map={
                    'new': '#FF6B6B',
                    'in-progress': '#4ECDC4',
                    'closed': '#45B7D1',
                    'rejected': '#96CEB4'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Campaign performance
            st.markdown("**Campaign Performance**")
            campaign_counts = df['campaign_tag'].value_counts().head(10)
            
            fig_campaign = px.bar(
                x=campaign_counts.index,
                y=campaign_counts.values,
                title="Leads by Campaign",
                labels={'x': 'Campaign', 'y': 'Count'}
            )
            fig_campaign.update_xaxes(tickangle=45)
            st.plotly_chart(fig_campaign, use_container_width=True)
        
        # Detailed analytics
        st.markdown("### Detailed Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Lead Status Summary**")
            status_summary = df['lead_status'].value_counts()
            st.dataframe(status_summary.reset_index().rename(
                columns={'index': 'Status', 'lead_status': 'Count'}
            ), use_container_width=True)
        
        with col2:
            st.markdown("**Top Campaigns**")
            campaign_summary = df['campaign_tag'].value_counts().head(10)
            st.dataframe(campaign_summary.reset_index().rename(
                columns={'index': 'Campaign', 'campaign_tag': 'Count'}
            ), use_container_width=True)
        
        # Timeline analysis
        if 'assigned_date' in df.columns:
            st.markdown("### Lead Timeline Analysis")
            
            # Group by date and count leads
            df['assigned_date'] = pd.to_datetime(df['assigned_date'])
            df['date'] = df['assigned_date'].dt.date
            
            timeline_data = df.groupby(['date', 'lead_status']).size().reset_index(name='count')
            
            fig_timeline = px.line(
                timeline_data,
                x='date',
                y='count',
                color='lead_status',
                title="Lead Creation Timeline",
                labels={'date': 'Date', 'count': 'Leads', 'lead_status': 'Status'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Performance metrics
        st.markdown("### Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_leads = len(df)
            closed_leads = len(df[df['lead_status'] == 'closed'])
            success_rate = round((closed_leads / total_leads) * 100, 1) if total_leads > 0 else 0
            st.metric("Success Rate", f"{success_rate}%")
        
        with col2:
            avg_processing_time = "N/A"  # Would need more data to calculate
            st.metric("Avg Processing Time", avg_processing_time)
        
        with col3:
            active_leads = len(df[df['lead_status'].isin(['new', 'in-progress'])])
            st.metric("Active Leads", active_leads)
        
        # Bank-wise analysis
        if 'bank_name' in df.columns:
            st.markdown("### Bank-wise Analysis")
            
            bank_stats = df['bank_name'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Leads by Bank**")
                st.dataframe(bank_stats.reset_index().rename(
                    columns={'index': 'Bank', 'bank_name': 'Count'}
                ), use_container_width=True)
            
            with col2:
                fig_bank = px.pie(
                    values=bank_stats.values,
                    names=bank_stats.index,
                    title="Leads by Bank"
                )
                st.plotly_chart(fig_bank, use_container_width=True)
    
    else:
        st.info("No leads data available for analytics. Create some leads first!")

def main():
    """Main lead management function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - Lead Management",
        page_icon="🎯",
        layout="wide"
    )
    
    # Show lead management page
    show_lead_management()

if __name__ == "__main__":
    main() 