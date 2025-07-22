#!/usr/bin/env python3
"""
Script to load MIS data from the data folder into the database
This replaces the upload functionality with a direct data loading approach
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from backend.db import get_db_connection, init_db
from backend.mis import validate_mis_data, process_mis_data, extract_username_from_campaign_id, is_dsa_campaign

def load_mis_data_from_file():
    """Load MIS data from the data folder"""
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized successfully!")
        
        # Path to the MIS file
        mis_file_path = "data/PPIPL HSBC MIS.xlsx"
        
        if not os.path.exists(mis_file_path):
            print(f"❌ Error: MIS file not found at {mis_file_path}")
            return False
        
        print(f"📁 Loading MIS data from: {mis_file_path}")
        
        # Read the Excel file from the 'Main' sheet
        try:
            df = pd.read_excel(mis_file_path, sheet_name='Main', engine='openpyxl')
            print(f"✅ Successfully read Excel file (Main sheet) with {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            return False
        
        # Validate the data structure
        is_valid, message = validate_mis_data(df)
        if not is_valid:
            print(f"❌ Data validation failed: {message}")
            return False
        
        print(f"✅ Data validation successful: {message}")
        
        # Process and store the data
        # Use admin user (ID=1) as the uploader
        success, result = process_mis_data(df, uploaded_by=1, created_by="admin", file_name="PPIPL_HSBC_MIS.xlsx")
        
        if success:
            print(f"✅ Successfully loaded MIS data: {result}")
            return True
        else:
            print(f"❌ Failed to load MIS data: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def analyze_mis_data():
    """Analyze the MIS data to show what's in it"""
    try:
        mis_file_path = "data/PPIPL HSBC MIS.xlsx"
        
        if not os.path.exists(mis_file_path):
            print(f"❌ Error: MIS file not found at {mis_file_path}")
            return
        
        print(f"📊 Analyzing MIS data from: {mis_file_path}")
        
        # Read the Excel file from the 'Main' sheet
        df = pd.read_excel(mis_file_path, sheet_name='Main', engine='openpyxl')
        
        print(f"\n📋 File Overview:")
        print(f"   - Total rows: {len(df):,}")
        print(f"   - Total columns: {len(df.columns)}")
        print(f"   - File size: {os.path.getsize(mis_file_path) / (1024*1024):.2f} MB")
        
        print(f"\n📝 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Analyze FORM CAMPAIGN_ID column
        if 'FORM CAMPAIGN_ID' in df.columns:
            campaign_ids = df['FORM CAMPAIGN_ID'].dropna().unique()
            print(f"\n🎯 FORM CAMPAIGN_ID Analysis:")
            print(f"   - Unique campaign IDs: {len(campaign_ids)}")
            
            # Show first 10 campaign IDs
            print(f"   - Sample campaign IDs:")
            for i, campaign_id in enumerate(campaign_ids[:10], 1):
                dsa_username = extract_username_from_campaign_id(campaign_id)
                is_dsa = is_dsa_campaign(campaign_id)
                print(f"     {i:2d}. {campaign_id} -> DSA: {dsa_username or 'None'} (DSA: {is_dsa})")
            
            # Count DSA vs System campaigns
            dsa_campaigns = [cid for cid in campaign_ids if is_dsa_campaign(cid)]
            system_campaigns = [cid for cid in campaign_ids if not is_dsa_campaign(cid)]
            
            print(f"\n📊 Campaign Type Breakdown:")
            print(f"   - DSA Campaigns: {len(dsa_campaigns)}")
            print(f"   - System Campaigns: {len(system_campaigns)}")
            
            if dsa_campaigns:
                print(f"   - DSA Usernames found:")
                dsa_usernames = set()
                for campaign_id in dsa_campaigns:
                    username = extract_username_from_campaign_id(campaign_id)
                    if username:
                        dsa_usernames.add(username)
                
                for username in sorted(dsa_usernames):
                    print(f"     • {username}")
        
        # Show sample data
        print(f"\n📄 Sample Data (first 3 rows):")
        print(df.head(3).to_string())
        
    except Exception as e:
        print(f"❌ Error analyzing MIS data: {e}")

if __name__ == "__main__":
    print("🏦 HSBC BTL Tracking - MIS Data Loader")
    print("=" * 50)
    
    # Check if data file exists
    if not os.path.exists("data/PPIPL HSBC MIS.xlsx"):
        print("❌ Error: MIS file not found in data folder")
        print("Please ensure 'PPIPL HSBC MIS.xlsx' is in the 'data' folder")
        sys.exit(1)
    
    # Ask user what to do
    print("\nChoose an option:")
    print("1. Analyze MIS data (show file contents)")
    print("2. Load MIS data into database")
    print("3. Both analyze and load")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            analyze_mis_data()
        elif choice == "2":
            if load_mis_data_from_file():
                print("\n🎉 MIS data loaded successfully!")
            else:
                print("\n❌ Failed to load MIS data")
                sys.exit(1)
        elif choice == "3":
            analyze_mis_data()
            print("\n" + "="*50)
            if load_mis_data_from_file():
                print("\n🎉 MIS data loaded successfully!")
            else:
                print("\n❌ Failed to load MIS data")
                sys.exit(1)
        else:
            print("❌ Invalid choice. Please run the script again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 