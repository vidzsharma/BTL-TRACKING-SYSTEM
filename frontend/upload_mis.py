import streamlit as st
import pandas as pd
from frontend.helpers import (
    upload_mis_file, get_mis_data, validate_file_upload,
    display_success_message, display_error_message, display_info_message,
    format_datetime, create_metrics_dataframe
)

def show_mis_upload():
    """Display MIS upload page"""
    st.title("📁 MIS Management")
    st.markdown("---")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📤 Upload MIS", "📊 View MIS Data", "📋 MIS Statistics"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_mis_data_section()
    
    with tab3:
        show_mis_statistics_section()

def show_upload_section():
    """Show MIS upload section"""
    st.subheader("📤 Upload MIS File")
    st.markdown("Upload your campaign data in CSV or Excel format.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel files containing campaign data"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"**File:** {uploaded_file.name} | **Size:** {uploaded_file.size} bytes")
        
        # Validate file
        is_valid, validation_message = validate_file_upload(uploaded_file)
        
        if is_valid:
            st.success(validation_message)
            
            # Preview data
            st.subheader("📋 Data Preview")
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df.head(10), use_container_width=True)
                st.info(f"Total rows: {len(df)} | Total columns: {len(df.columns)}")
                
                # Check required columns
                required_columns = ['bank', 'username', 'team_leader_name', 'email_id', 'campaign_tag']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.warning(f"⚠️ Missing required columns: {', '.join(missing_columns)}")
                    st.info("Required columns: bank, username, team_leader_name, email_id, campaign_tag")
                else:
                    st.success("✅ All required columns are present")
                
                # Upload button
                if st.button("🚀 Upload MIS Data", type="primary"):
                    with st.spinner("Uploading MIS data..."):
                        success, result = upload_mis_file(uploaded_file)
                        
                        if success:
                            display_success_message("MIS data uploaded successfully!")
                            
                            # Display upload results
                            if isinstance(result, dict):
                                st.markdown("### Upload Summary")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Total Rows", result.get('total_rows', 0))
                                
                                with col2:
                                    st.metric("Successfully Processed", result.get('success_count', 0))
                                
                                with col3:
                                    st.metric("Errors", result.get('error_count', 0))
                                
                                if result.get('error_count', 0) > 0:
                                    st.warning(f"Some rows had errors during processing. Please check your data.")
                        else:
                            display_error_message(f"Upload failed: {result}")
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        else:
            st.error(validation_message)

def show_mis_data_section():
    """Show MIS data viewing section"""
    st.subheader("📊 View MIS Data")
    
    # Load MIS data
    with st.spinner("Loading MIS data..."):
        mis_data = get_mis_data()
    
    if mis_data:
        # Convert to DataFrame
        df = create_metrics_dataframe(mis_data)
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Campaign filter
            campaigns = ['All'] + sorted(df['campaign_tag'].unique().tolist())
            selected_campaign = st.selectbox("Campaign", campaigns)
        
        with col2:
            # Bank filter
            banks = ['All'] + sorted(df['bank'].unique().tolist())
            selected_bank = st.selectbox("Bank", banks)
        
        with col3:
            # Date range filter
            if 'uploaded_at' in df.columns:
                df['uploaded_at'] = pd.to_datetime(df['uploaded_at'])
                min_date = df['uploaded_at'].min()
                max_date = df['uploaded_at'].max()
                
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_campaign != 'All':
            filtered_df = filtered_df[filtered_df['campaign_tag'] == selected_campaign]
        
        if selected_bank != 'All':
            filtered_df = filtered_df[filtered_df['bank'] == selected_bank]
        
        if 'uploaded_at' in filtered_df.columns and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['uploaded_at'].dt.date >= start_date) &
                (filtered_df['uploaded_at'].dt.date <= end_date)
            ]
        
        # Display filtered data
        st.markdown(f"### MIS Data ({len(filtered_df)} records)")
        
        # Show key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(filtered_df))
        
        with col2:
            unique_campaigns = filtered_df['campaign_tag'].nunique()
            st.metric("Unique Campaigns", unique_campaigns)
        
        with col3:
            unique_banks = filtered_df['bank'].nunique()
            st.metric("Unique Banks", unique_banks)
        
        with col4:
            unique_users = filtered_df['username'].nunique()
            st.metric("Unique Users", unique_users)
        
        # Data table
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"mis_data_{selected_campaign}_{selected_bank}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("No MIS data available. Please upload some data first.")

def show_mis_statistics_section():
    """Show MIS statistics section"""
    st.subheader("📋 MIS Statistics")
    
    # Load MIS data for statistics
    with st.spinner("Loading MIS statistics..."):
        mis_data = get_mis_data()
    
    if mis_data:
        df = create_metrics_dataframe(mis_data)
        
        # Statistics overview
        st.markdown("### Overview Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Campaign statistics
            st.markdown("**Campaign Statistics**")
            campaign_stats = df['campaign_tag'].value_counts()
            
            # Create bar chart for campaigns
            import plotly.express as px
            fig_campaign = px.bar(
                x=campaign_stats.index,
                y=campaign_stats.values,
                title="Records by Campaign",
                labels={'x': 'Campaign', 'y': 'Count'}
            )
            st.plotly_chart(fig_campaign, use_container_width=True)
        
        with col2:
            # Bank statistics
            st.markdown("**Bank Statistics**")
            bank_stats = df['bank'].value_counts()
            
            # Create pie chart for banks
            fig_bank = px.pie(
                values=bank_stats.values,
                names=bank_stats.index,
                title="Records by Bank"
            )
            st.plotly_chart(fig_bank, use_container_width=True)
        
        # Detailed statistics
        st.markdown("### Detailed Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Campaigns**")
            top_campaigns = df['campaign_tag'].value_counts().head(10)
            st.dataframe(top_campaigns.reset_index().rename(
                columns={'index': 'Campaign', 'campaign_tag': 'Count'}
            ), use_container_width=True)
        
        with col2:
            st.markdown("**Top Banks**")
            top_banks = df['bank'].value_counts().head(10)
            st.dataframe(top_banks.reset_index().rename(
                columns={'index': 'Bank', 'bank': 'Count'}
            ), use_container_width=True)
        
        # Upload timeline
        if 'uploaded_at' in df.columns:
            st.markdown("### Upload Timeline")
            
            # Group by date and count uploads
            df['upload_date'] = pd.to_datetime(df['uploaded_at']).dt.date
            upload_timeline = df.groupby('upload_date').size().reset_index(name='count')
            
            fig_timeline = px.line(
                upload_timeline,
                x='upload_date',
                y='count',
                title="MIS Uploads Over Time",
                labels={'upload_date': 'Date', 'count': 'Uploads'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Team leader statistics
        if 'team_leader_name' in df.columns:
            st.markdown("### Team Leader Performance")
            
            team_leader_stats = df['team_leader_name'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Records by Team Leader**")
                st.dataframe(team_leader_stats.reset_index().rename(
                    columns={'index': 'Team Leader', 'team_leader_name': 'Count'}
                ), use_container_width=True)
            
            with col2:
                fig_team = px.bar(
                    x=team_leader_stats.index,
                    y=team_leader_stats.values,
                    title="Records by Team Leader",
                    labels={'x': 'Team Leader', 'y': 'Count'}
                )
                fig_team.update_xaxes(tickangle=45)
                st.plotly_chart(fig_team, use_container_width=True)
    
    else:
        st.info("No MIS data available for statistics. Please upload some data first.")

def main():
    """Main MIS upload function"""
    # Page configuration
    st.set_page_config(
        page_title="BTL Tracking - MIS Management",
        page_icon="📁",
        layout="wide"
    )
    
    # Show MIS upload page
    show_mis_upload()

if __name__ == "__main__":
    main() 