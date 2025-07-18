#!/usr/bin/env python3
"""
Test script to check all imports
"""

def test_imports():
    """Test all the imports that are failing"""
    print("🧪 Testing all imports...")
    
    try:
        print("1. Testing frontend.helpers...")
        from frontend.helpers import (
            login_user, display_error_message, display_success_message,
            get_mis_data, get_leads_data, get_performance_data,
            get_team_members, get_user_role, format_datetime,
            create_metrics_dataframe, create_lead, update_lead_progress,
            get_lead_details, get_lead_status_options
        )
        print("✅ All helper functions imported successfully!")
        
        print("2. Testing frontend modules...")
        from frontend.login import show_login_page
        print("✅ Login module imported!")
        
        from frontend.dashboard import show_dashboard
        print("✅ Dashboard module imported!")
        
        from frontend.upload_mis import show_mis_upload
        print("✅ Upload MIS module imported!")
        
        from frontend.lead_management import show_lead_management
        print("✅ Lead management module imported!")
        
        from frontend.team_progress import show_team_progress
        print("✅ Team progress module imported!")
        
        from frontend.team_management import show_team_management
        print("✅ Team management module imported!")
        
        from frontend.reports import show_reports
        print("✅ Reports module imported!")
        
        print("\n🎉 All imports successful! Application should work now.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🚀 Ready to start the application!")
        print("Run: python start_app.py")
    else:
        print("\n❌ There are still import issues to fix.") 