import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask import request, jsonify
from backend.db import get_db_cursor, close_db_connection
from config import Config
import json

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def parse_excel_file(file_path):
    """Parse Excel file and return DataFrame"""
    try:
        # Try to read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        return df
    except Exception as e:
        print(f"Error parsing Excel file: {e}")
        return None

def parse_csv_file(file_path):
    """Parse CSV file and return DataFrame"""
    try:
        # Try to read CSV file with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
        return None
    except Exception as e:
        print(f"Error parsing CSV file: {e}")
        return None

def validate_mis_data(df):
    """Validate MIS data structure"""
    required_columns = ['bank', 'username', 'team_leader_name', 'email_id', 'campaign_tag']
    
    # Check if required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    # Check for empty values in required fields
    for col in required_columns:
        if df[col].isnull().any():
            return False, f"Empty values found in column: {col}"
    
    return True, "Data validation successful"

def process_mis_data(df, uploaded_by, file_name):
    """Process and store MIS data in database"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return False, "Database connection failed"
    
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
                cursor.execute("""
                    INSERT INTO mis_data 
                    (bank, username, team_leader_name, email_id, campaign_tag, uploaded_by, file_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(row['bank']),
                    str(row['username']),
                    str(row['team_leader_name']),
                    str(row['email_id']),
                    str(row['campaign_tag']),
                    uploaded_by,
                    file_name
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
        close_db_connection(conn, cursor)

def upload_mis_file(file, uploaded_by):
    """Upload and process MIS file"""
    if file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, "File type not allowed. Please upload CSV or Excel files."
    
    # Create upload directory if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Secure filename and save file
    filename = secure_filename(file.filename)
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    try:
        file.save(file_path)
        
        # Parse file based on extension
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension in ['xlsx', 'xls']:
            df = parse_excel_file(file_path)
        elif file_extension == 'csv':
            df = parse_csv_file(file_path)
        else:
            return False, "Unsupported file format"
        
        if df is None:
            return False, "Error parsing file"
        
        # Process the data
        success, result = process_mis_data(df, uploaded_by, filename)
        
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return success, result
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        return False, f"Error uploading file: {str(e)}"

def get_mis_data(user_id, role, team_leader_id=None):
    """Get MIS data based on user role"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return []
    
    try:
        if role == 'admin':
            # Admin can see all MIS data
            cursor.execute("""
                SELECT md.*, u.username as uploaded_by_username
                FROM mis_data md
                LEFT JOIN users u ON md.uploaded_by = u.user_id
                ORDER BY md.uploaded_at DESC
            """)
        elif role == 'team_leader':
            # Team leader can see MIS data for their team
            cursor.execute("""
                SELECT md.*, u.username as uploaded_by_username
                FROM mis_data md
                LEFT JOIN users u ON md.uploaded_by = u.user_id
                WHERE md.team_leader_name IN (
                    SELECT username FROM users WHERE team_leader_id = %s
                ) OR md.uploaded_by = %s
                ORDER BY md.uploaded_at DESC
            """, (team_leader_id, user_id))
        else:
            # Regular user can see MIS data they uploaded
            cursor.execute("""
                SELECT md.*, u.username as uploaded_by_username
                FROM mis_data md
                LEFT JOIN users u ON md.uploaded_by = u.user_id
                WHERE md.uploaded_by = %s
                ORDER BY md.uploaded_at DESC
            """, (user_id,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting MIS data: {e}")
        return []
    finally:
        close_db_connection(conn, cursor)

def get_mis_statistics(user_id, role, team_leader_id=None):
    """Get MIS statistics for dashboard"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return {}
    
    try:
        if role == 'admin':
            # Admin statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT campaign_tag) as total_campaigns,
                    COUNT(DISTINCT team_leader_name) as total_team_leaders,
                    COUNT(DISTINCT bank) as total_banks,
                    DATE(MAX(uploaded_at)) as last_upload_date
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
                    DATE(MAX(uploaded_at)) as last_upload_date
                FROM mis_data
                WHERE team_leader_name IN (
                    SELECT username FROM users WHERE team_leader_id = %s
                ) OR uploaded_by = %s
            """, (team_leader_id, user_id))
        else:
            # User statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT campaign_tag) as total_campaigns,
                    COUNT(DISTINCT bank) as total_banks,
                    DATE(MAX(uploaded_at)) as last_upload_date
                FROM mis_data
                WHERE uploaded_by = %s
            """, (user_id,))
        
        stats = cursor.fetchone()
        return dict(stats) if stats else {}
        
    except Exception as e:
        print(f"Error getting MIS statistics: {e}")
        return {}
    finally:
        close_db_connection(conn, cursor)

def get_campaign_data(campaign_tag, user_id, role, team_leader_id=None):
    """Get data for specific campaign"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return []
    
    try:
        if role == 'admin':
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = %s
                ORDER BY uploaded_at DESC
            """, (campaign_tag,))
        elif role == 'team_leader':
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = %s AND (
                    team_leader_name IN (
                        SELECT username FROM users WHERE team_leader_id = %s
                    ) OR uploaded_by = %s
                )
                ORDER BY uploaded_at DESC
            """, (campaign_tag, team_leader_id, user_id))
        else:
            cursor.execute("""
                SELECT * FROM mis_data 
                WHERE campaign_tag = %s AND uploaded_by = %s
                ORDER BY uploaded_at DESC
            """, (campaign_tag, user_id))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting campaign data: {e}")
        return []
    finally:
        close_db_connection(conn, cursor) 