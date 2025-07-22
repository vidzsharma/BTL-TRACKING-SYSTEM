import pandas as pd
import os
from backend.db import get_db_connection, get_user_by_id, get_team_members
from config import Config
import json

def validate_mis_data(df):
    """Validate MIS data structure for HSBC MIS file"""
    # Check if FORM CAMPAIGN_ID exists (this is the key field for filtering)
    if 'FORM CAMPAIGN_ID' not in df.columns:
        return False, "Missing required column: FORM CAMPAIGN_ID"
    
    # Check if other important columns exist
    important_columns = ['APPLICATION STATUS', 'CARD TYPE', 'Status', 'LEAD ID']
    missing_columns = [col for col in important_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns: {missing_columns}")
    
    return True, "Data validation successful"

def process_mis_data(df, uploaded_by, created_by, file_name):
    """Process and store MIS data in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Validate data
        is_valid, message = validate_mis_data(df)
        if not is_valid:
            return False, message
        
        # Process each row
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract username from FORM CAMPAIGN_ID
                form_campaign_id = str(row.get('FORM CAMPAIGN_ID', ''))
                username = extract_username_from_campaign_id(form_campaign_id)
                
                # For now, process all campaigns (including system campaigns)
                # When DSA campaigns are available, this will filter them properly
                if not is_dsa_campaign(form_campaign_id):
                    print(f"Processing system campaign: {form_campaign_id}")
                    # Don't skip system campaigns for now since that's all we have
                
                cursor.execute("""
                    INSERT INTO mis_data 
                    (data_type, data_received_month, file_received_date, data_received_date,
                     application_number, lead_id, adobe_lead_id, creation_date_time, 
                     last_updated_date_time, apps_ref_number, form_source, form_campaign_id,
                     wt_ac, gclid, application_status, dip_status, customer_dropped_page,
                     lead_generation_stage, card_type, channel, frn_number, device_type,
                     browser, has_skipped_perfios, campaign, process_flag, 
                     vaibhav_journey_completed_dropoff, status, disposition, called_date,
                     remarks, attempt, frn, signzy, signzy_date, agent_remark_vicp,
                     vcip_auto_login_url, stb_status, stb_date, booking_date, booking_status,
                     remarks_1, decline_class, decline_category, booking_month, 
                     final_channel_flag1, decline_code, declined_by, decline_description,
                     cj, cj_received_date, cj_status, cj_remarks, upload_date_field,
                     wip_que_name, creation_month, creation_date, as_per_creation_date,
                     as_per_vcip_completed, company_name, username, team_leader_name,
                     uploaded_by, created_by, file_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    str(row.get('Data Type', '')),
                    str(row.get('Data Received Month', '')),
                    str(row.get('File-Recived-Date', '')),
                    str(row.get('data received date', '')),
                    str(row.get('APPLICATION NUMBER', '')),
                    str(row.get('LEAD ID', '')),
                    str(row.get('ADOBE LEAD ID', '')),
                    str(row.get('CREATION DATE/TIME', '')),
                    str(row.get('LAST UPDATED DATE/TIME', '')),
                    str(row.get('APPS REF NUMBER', '')),
                    str(row.get('FORM:SOURCE', '')),
                    form_campaign_id,
                    str(row.get('WT:AC', '')),
                    str(row.get('GCLID', '')),
                    str(row.get('APPLICATION STATUS', '')),
                    str(row.get('DIP  STATUS', '')),
                    str(row.get('CUSTOMER DROPPED PAGE', '')),
                    str(row.get('LEAD GENERATION STAGE', '')),
                    str(row.get('CARD TYPE', '')),
                    str(row.get('CHANNEL', '')),
                    str(row.get('FRN NUMBER', '')),
                    str(row.get('DEVICE TYPE', '')),
                    str(row.get('BROWSER', '')),
                    str(row.get('HAS SKIPPED PERFIOS', '')),
                    str(row.get('Campaign', '')),
                    str(row.get('Process-Flag', '')),
                    str(row.get('vaibhav Journey-completed-/-Drop-off', '')),
                    str(row.get('Status', '')),
                    str(row.get('Disposition', '')),
                    str(row.get('Called-Date', '')),
                    str(row.get('Remarks', '')),
                    str(row.get('Attempt', '')),
                    str(row.get('FRN', '')),
                    str(row.get('Signzy', '')),
                    str(row.get('Signzy-Date', '')),
                    str(row.get('Agent-Remark-VICP', '')),
                    str(row.get('VCIP-Auto-login-URL', '')),
                    str(row.get('STB-Status', '')),
                    str(row.get('STB Date', '')),
                    str(row.get('Booking-Date', '')),
                    str(row.get('Booking-Status', '')),
                    str(row.get('Remarks.1', '')),
                    str(row.get('DECLINE_CLASS', '')),
                    str(row.get('DECLINE_CATEGORY', '')),
                    str(row.get('Booking-Month', '')),
                    str(row.get('FINAL_CHANNEL_FLAG1', '')),
                    str(row.get('Decline-Code', '')),
                    str(row.get('Declined-By', '')),
                    str(row.get('Decline-Description', '')),
                    str(row.get('CJ', '')),
                    str(row.get('CJ-Received-Date', '')),
                    str(row.get('CJ-Status', '')),
                    str(row.get('CJ-Remarks', '')),
                    str(row.get('Upload date', '')),
                    str(row.get('WIP Que Name', '')),
                    str(row.get('CREATION Month', '')),
                    str(row.get('CREATION DATE', '')),
                    str(row.get('As Per Creation Date', '')),
                                    str(row.get('AS Per VCIP Completed', '')),
                str(row.get('COMPANY Name', '')),
                username,
                str(row.get('team_leader_name', '')),
                uploaded_by,
                created_by
                ))
                success_count += 1
                
            except Exception as e:
                print(f"Error inserting row {index}: {e}")
                error_count += 1
                continue
        
        conn.commit()
        
        return True, {
            "message": "MIS data processed successfully",
            "success_count": success_count,
            "error_count": error_count,
            "total_rows": len(df)
        }
        
    except Exception as e:
        print(f"Error processing MIS data: {e}")
        conn.rollback()
        return False, f"Error processing data: {str(e)}"
    finally:
        conn.close()

def extract_username_from_campaign_id(campaign_id):
    """Extract DSA username from FORM CAMPAIGN_ID"""
    if not campaign_id:
        return ''
    
    campaign_id = str(campaign_id).upper()  # Convert to uppercase for case-insensitive matching
    
    # Check if it starts with PPIPL_
    if not campaign_id.startswith('PPIPL_'):
        return ''
    
    # Remove PPIPL_ prefix
    campaign_part = campaign_id[6:]  # Remove "PPIPL_"
    
    # Define NON-DSA patterns that should be filtered out
    non_dsa_patterns = ['CHKR', 'ENKR', 'AF', 'PS', 'CCCAMPAIGN', 'TQ', 'BNKR', 'FBA', 'PAID']
    
    # If it contains any non-DSA pattern, return empty (not a DSA lead)
    for pattern in non_dsa_patterns:
        if pattern in campaign_part:
            return ''
    
    # Extract DSA username (e.g., PPIPL_RPM001 -> RPM001)
    # The DSA username is the part after PPIPL_ that doesn't contain non-DSA patterns
    parts = campaign_part.split('_')
    if parts and parts[0]:
        # Check if this looks like a DSA ID (contains letters and numbers)
        dsa_id = parts[0]
        if len(dsa_id) >= 3 and any(c.isdigit() for c in dsa_id) and any(c.isalpha() for c in dsa_id):
            return dsa_id
    
    return ''

def is_dsa_campaign(campaign_id):
    """Check if FORM CAMPAIGN_ID belongs to a DSA (not system campaigns)"""
    if not campaign_id:
        return False
    
    campaign_id = str(campaign_id).upper()
        
    # Non-DSA patterns that should be filtered out
    non_dsa_patterns = ['CHKR', 'ENKR', 'AF', 'PS', 'CCCAMPAIGN', 'TQ', 'BNKR', 'FBA', 'PAID']
    
    # Check if it contains any non-DSA pattern
    for pattern in non_dsa_patterns:
        if pattern in campaign_id:
            return False
    
    return True



def get_mis_data(user_id, role, team_leader_id=None):
    """Get MIS data based on user role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            # Admin can see all MIS data (including system campaigns)
            cursor.execute("""
                SELECT md.*, u.username as uploaded_by_username
                FROM mis_data md
                LEFT JOIN users u ON md.uploaded_by = u.id
                ORDER BY md.upload_date DESC
            """)
        elif role == 'team_leader':
            # Team leader can see their team members' DSA leads and system campaigns
            user = get_user_by_id(user_id)
            username = user['username'] if user else ''
            
            # Get team member usernames
            team_members = get_team_members(team_leader_id)
            team_usernames = [member['username'] for member in team_members]
            
            if team_usernames:
                # Build query to show team members' DSA leads and system campaigns
                team_conditions = ' OR '.join([f"md.form_campaign_id LIKE '%{member}%'" for member in team_usernames])
                cursor.execute(f"""
                    SELECT md.*, u.username as uploaded_by_username
                    FROM mis_data md
                    LEFT JOIN users u ON md.uploaded_by = u.id
                    WHERE ({team_conditions}) OR md.uploaded_by = ?
                    ORDER BY md.upload_date DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT md.*, u.username as uploaded_by_username
                    FROM mis_data md
                    LEFT JOIN users u ON md.uploaded_by = u.id
                    WHERE md.uploaded_by = ?
                    ORDER BY md.upload_date DESC
                """, (user_id,))
        else:
            # Regular user can only see their own DSA leads (filter out system campaigns)
            user = get_user_by_id(user_id)
            username = user['username'] if user else ''
            
            # Filter by username in the mis_data table
            cursor.execute("""
                SELECT md.*, u.username as uploaded_by_username
                FROM mis_data md
                LEFT JOIN users u ON md.uploaded_by = u.id
                WHERE md.username = ?
                ORDER BY md.upload_date DESC
            """, (username,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting MIS data: {e}")
        return []
    finally:
        conn.close()

def get_username_by_id(user_id):
    """Get username by user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return result['username'] if result else None
    except Exception as e:
        print(f"Error getting username: {e}")
        return None
    finally:
        conn.close()

def get_mis_statistics(user_id, role, team_leader_id=None):
    """Get MIS statistics for dashboard based on role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            # Admin statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT campaign_tag) as total_campaigns,
                    COUNT(DISTINCT team_leader_name) as total_team_leaders,
                    COUNT(DISTINCT bank) as total_banks,
                    DATE(MAX(upload_date)) as last_upload_date
                FROM mis_data
            """)
        elif role == 'team_leader':
            # Team leader statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT campaign_tag) as total_campaigns,
                    COUNT(DISTINCT username) as total_team_members,
                    COUNT(DISTINCT bank) as total_banks,
                    DATE(MAX(upload_date)) as last_upload_date
                FROM mis_data
                WHERE team_leader_name IN (
                    SELECT username FROM users WHERE team_leader_id = ?
                ) OR uploaded_by = ?
            """, (team_leader_id, user_id))
        else:
            # User statistics - only for their campaigns
            username = get_username_by_id(user_id)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT campaign_tag) as total_campaigns,
                    COUNT(DISTINCT bank) as total_banks,
                    DATE(MAX(upload_date)) as last_upload_date
                FROM mis_data
                WHERE username = ?
            """, (username,))
        
        stats = cursor.fetchone()
        return dict(stats) if stats else {}
        
    except Exception as e:
        print(f"Error getting MIS statistics: {e}")
        return {}
    finally:
        conn.close()

def get_campaign_data(campaign_tag, user_id, role, team_leader_id=None):
    """Get data for specific campaign based on role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = ?
                ORDER BY upload_date DESC
            """, (campaign_tag,))
        elif role == 'team_leader':
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = ? AND (
                    team_leader_name IN (
                        SELECT username FROM users WHERE team_leader_id = ?
                    ) OR uploaded_by = ?
                )
                ORDER BY upload_date DESC
            """, (campaign_tag, team_leader_id, user_id))
        else:
            # User can only see campaigns where their username appears
            username = get_username_by_id(user_id)
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = ? AND username = ?
                ORDER BY upload_date DESC
            """, (campaign_tag, username))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting campaign data: {e}")
        return []
    finally:
        conn.close() 