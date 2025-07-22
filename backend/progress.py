from backend.db import get_db_connection
from datetime import datetime, timedelta
import json

def create_lead(user_id, campaign_tag, customer_name=None, customer_phone=None, customer_email=None, bank_name=None, created_by=None):
    """Create a new lead with created_by field"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO leads 
            (customer_name, phone_number, email, card_type, application_date, status, assigned_to, created_by, campaign_tag, bank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_name,
            customer_phone,
            customer_email,
            'Credit Card',  # Default card type
            datetime.now().date(),
            'new',
            user_id,
            created_by,
            campaign_tag,
            bank_name
        ))
        
        lead_id = cursor.lastrowid
        conn.commit()
        
        return True, {"lead_id": lead_id, "message": "Lead created successfully"}
        
    except Exception as e:
        print(f"Error creating lead: {e}")
        conn.rollback()
        return False, f"Error creating lead: {str(e)}"
    finally:
        conn.close()

def update_lead_progress(lead_id, user_id, progress_status, progress_notes=None):
    """Update lead progress"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user has access to this lead
        cursor.execute("""
            SELECT created_by, assigned_to FROM leads WHERE id = ?
        """, (lead_id,))
        
        lead = cursor.fetchone()
        if not lead:
            return False, "Lead not found"
        
        # Check access permissions
        if lead['created_by'] != get_username_by_id(user_id) and lead['assigned_to'] != user_id:
            return False, "Access denied to this lead"
        
        # Update lead status
        cursor.execute("""
            UPDATE leads 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (progress_status, lead_id))
        
        if cursor.rowcount == 0:
            return False, "Lead not found or access denied"
        
        # Add progress tracking record
        cursor.execute("""
            INSERT INTO progress_tracking 
            (user_id, date, notes)
            VALUES (?, ?, ?)
        """, (user_id, datetime.now().date(), progress_notes))
        
        conn.commit()
        return True, "Progress updated successfully"
        
    except Exception as e:
        print(f"Error updating lead progress: {e}")
        conn.rollback()
        return False, f"Error updating progress: {str(e)}"
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

def get_user_leads(user_id, role, team_leader_id=None, status_filter=None, team_member=None):
    """Get leads based on user role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build the base query
        base_query = """
            SELECT 
                l.*,
                u.username as assigned_username
            FROM leads l
            LEFT JOIN users u ON l.assigned_to = u.id
            WHERE 1=1
        """
        params = []
        
        # Add role-based filtering
        if role == 'admin':
            # Admin can see all leads
            pass
        elif role == 'team_leader':
            # Team leader can see team members' leads
            if team_member and team_member != 'All Team Members':
                # Filter by specific team member
                base_query += " AND (l.created_by = ? OR l.assigned_to = (SELECT id FROM users WHERE username = ?))"
                params.extend([team_member, team_member])
            else:
                # Show all team members' leads
                base_query += " AND (l.created_by IN (SELECT username FROM users WHERE team_leader_id = ?) OR l.assigned_to IN (SELECT id FROM users WHERE team_leader_id = ?) OR l.created_by = ? OR l.assigned_to = ?)"
                params.extend([team_leader_id, team_leader_id, get_username_by_id(user_id), user_id])
        else:
            # User can only see their own leads
            base_query += " AND (l.created_by = ? OR l.assigned_to = ?)"
            params.extend([get_username_by_id(user_id), user_id])
        
        # Add status filter if provided
        if status_filter:
            base_query += " AND l.status = ?"
            params.append(status_filter)
        
        # Add ordering
        base_query += " ORDER BY l.created_at DESC"
        
        cursor.execute(base_query, params)
        leads = cursor.fetchall()
        return [dict(lead) for lead in leads]
        
    except Exception as e:
        print(f"Error getting user leads: {e}")
        return []
    finally:
        conn.close()

def get_user_id_by_username(username):
    """Get user ID by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result['id'] if result else None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None
    finally:
        conn.close()

def get_lead_details(lead_id, user_id, role, team_leader_id=None):
    """Get detailed lead information with access control"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build query with role-based access
        if role == 'admin':
            cursor.execute("""
                SELECT 
                    l.*,
                    u.username as assigned_username
                FROM leads l
                LEFT JOIN users u ON l.assigned_to = u.id
                WHERE l.id = ?
            """, (lead_id,))
        elif role == 'team_leader':
            cursor.execute("""
                SELECT 
                    l.*,
                    u.username as assigned_username
                FROM leads l
                LEFT JOIN users u ON l.assigned_to = u.id
                WHERE l.id = ? AND (
                    l.created_by IN (SELECT username FROM users WHERE team_leader_id = ?) OR
                    l.assigned_to IN (SELECT id FROM users WHERE team_leader_id = ?) OR
                    l.created_by = ? OR l.assigned_to = ?
                )
            """, (lead_id, team_leader_id, team_leader_id, get_username_by_id(user_id), user_id))
        else:
            cursor.execute("""
                SELECT 
                    l.*,
                    u.username as assigned_username
                FROM leads l
                LEFT JOIN users u ON l.assigned_to = u.id
                WHERE l.id = ? AND (l.created_by = ? OR l.assigned_to = ?)
            """, (lead_id, get_username_by_id(user_id), user_id))
        
        lead = cursor.fetchone()
        return dict(lead) if lead else None
        
    except Exception as e:
        print(f"Error getting lead details: {e}")
        return None
    finally:
        conn.close()

def get_team_member_usernames(team_leader_id):
    """Get usernames of team members"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT username FROM users 
            WHERE team_leader_id = ? AND is_active = 1
        """, (team_leader_id,))
        usernames = cursor.fetchall()
        return [row['username'] for row in usernames]
    except Exception as e:
        print(f"Error getting team member usernames: {e}")
        return []
    finally:
        conn.close()

def get_team_member_ids(team_leader_id):
    """Get IDs of team members"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id FROM users 
            WHERE team_leader_id = ? AND is_active = 1
        """, (team_leader_id,))
        ids = cursor.fetchall()
        return [row['id'] for row in ids]
    except Exception as e:
        print(f"Error getting team member IDs: {e}")
        return []
    finally:
        conn.close()

def get_progress_statistics(user_id, role, team_leader_id=None, days=30):
    """Get progress statistics based on role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        if role == 'admin':
            # Admin can see all statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_leads,
                    SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_leads,
                    SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_leads
                FROM leads
                WHERE created_at >= ?
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader can see team statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_leads,
                    SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_leads,
                    SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_leads
                FROM leads
                WHERE created_at >= ? AND (
                    created_by IN (SELECT username FROM users WHERE team_leader_id = ?) OR
                    assigned_to IN (SELECT id FROM users WHERE team_leader_id = ?) OR
                    created_by = ? OR assigned_to = ?
                )
            """, (start_date, team_leader_id, team_leader_id, get_username_by_id(user_id), user_id))
            
        else:
            # User can only see their own statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_leads,
                    SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_leads,
                    SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_leads
                FROM leads
                WHERE created_at >= ? AND (created_by = ? OR assigned_to = ?)
            """, (start_date, get_username_by_id(user_id), user_id))
        
        stats = cursor.fetchone()
        return dict(stats) if stats else {}
        
    except Exception as e:
        print(f"Error getting progress statistics: {e}")
        return {}
    finally:
        conn.close()

def get_campaign_progress(campaign_tag, user_id, role, team_leader_id=None):
    """Get campaign progress statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if role == 'admin':
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = ?
                GROUP BY status
            """, (campaign_tag,))
            
        elif role == 'team_leader':
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = ? AND (
                    created_by IN (SELECT username FROM users WHERE team_leader_id = ?) OR
                    assigned_to IN (SELECT id FROM users WHERE team_leader_id = ?) OR
                    created_by = ? OR assigned_to = ?
                )
                GROUP BY status
            """, (campaign_tag, team_leader_id, team_leader_id, get_username_by_id(user_id), user_id))
            
        else:
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = ? AND (created_by = ? OR assigned_to = ?)
                GROUP BY status
            """, (campaign_tag, get_username_by_id(user_id), user_id))
        
        progress = cursor.fetchall()
        return [dict(row) for row in progress]
        
    except Exception as e:
        print(f"Error getting campaign progress: {e}")
        return []
    finally:
        conn.close()

def get_user_performance(user_id, role, team_leader_id=None, days=30):
    """Get user performance data based on role hierarchy"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        if role == 'admin':
            # Admin can see all users' performance
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.id) as total_leads,
                    SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN l.status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.username = l.created_by OR u.id = l.assigned_to
                WHERE l.created_at >= ? OR l.created_at IS NULL
                GROUP BY u.id, u.username
                ORDER BY total_leads DESC
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader can see team members' performance
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.id) as total_leads,
                    SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN l.status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.username = l.created_by OR u.id = l.assigned_to
                WHERE (u.team_leader_id = ? OR u.id = ?) AND (l.created_at >= ? OR l.created_at IS NULL)
                GROUP BY u.id, u.username
                ORDER BY total_leads DESC
            """, (team_leader_id, user_id, start_date))
            
        else:
            # User can only see their own performance
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.id) as total_leads,
                    SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                    SUM(CASE WHEN l.status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.username = l.created_by OR u.id = l.assigned_to
                WHERE u.id = ? AND (l.created_at >= ? OR l.created_at IS NULL)
                GROUP BY u.id, u.username
            """, (user_id, start_date))
        
        performance = cursor.fetchall()
        return [dict(row) for row in performance]
        
    except Exception as e:
        print(f"Error getting user performance: {e}")
        return []
    finally:
        conn.close()

def get_mis_analytics(user_id, role, team_leader_id=None, days=30):
    """Get comprehensive MIS analytics with specific fields"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        if role == 'admin':
            # Admin sees all MIS data
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN application_status = 'APPROVED' THEN 1 ELSE 0 END) as approved_applications,
                    SUM(CASE WHEN application_status = 'PENDING' THEN 1 ELSE 0 END) as pending_applications,
                    SUM(CASE WHEN application_status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_applications,
                    AVG(CAST(attempt AS INTEGER)) as avg_attempts,
                    SUM(CASE WHEN card_type LIKE '%VISA%' OR card_type LIKE '%PLATINUM%' THEN 1 ELSE 0 END) as visa_platinum,
                    SUM(CASE WHEN card_type LIKE '%MASTERCARD%' THEN 1 ELSE 0 END) as mastercard,
                    COUNT(DISTINCT form_campaign_id) as unique_campaigns,
                    COUNT(DISTINCT customer_dropped_page) as unique_drop_pages,
                    COUNT(DISTINCT lead_generation_stage) as unique_stages
                FROM mis_data
                WHERE upload_date >= ?
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader sees team members' MIS data
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN application_status = 'APPROVED' THEN 1 ELSE 0 END) as approved_applications,
                    SUM(CASE WHEN application_status = 'PENDING' THEN 1 ELSE 0 END) as pending_applications,
                    SUM(CASE WHEN application_status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_applications,
                    AVG(CAST(attempt AS INTEGER)) as avg_attempts,
                    SUM(CASE WHEN card_type LIKE '%VISA%' OR card_type LIKE '%PLATINUM%' THEN 1 ELSE 0 END) as visa_platinum,
                    SUM(CASE WHEN card_type LIKE '%MASTERCARD%' THEN 1 ELSE 0 END) as mastercard,
                    COUNT(DISTINCT form_campaign_id) as unique_campaigns,
                    COUNT(DISTINCT customer_dropped_page) as unique_drop_pages,
                    COUNT(DISTINCT lead_generation_stage) as unique_stages
                FROM mis_data
                WHERE upload_date >= ? AND (
                    username IN (SELECT username FROM users WHERE team_leader_id = ?) OR
                    uploaded_by IN (SELECT id FROM users WHERE team_leader_id = ?) OR
                    uploaded_by = ? OR username = ?
                )
            """, (start_date, team_leader_id, team_leader_id, user_id, get_username_by_id(user_id)))
            
        else:
            # User sees only their own MIS data
            username = get_username_by_id(user_id)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN application_status = 'APPROVED' THEN 1 ELSE 0 END) as approved_applications,
                    SUM(CASE WHEN application_status = 'PENDING' THEN 1 ELSE 0 END) as pending_applications,
                    SUM(CASE WHEN application_status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_applications,
                    AVG(CAST(attempt AS INTEGER)) as avg_attempts,
                    SUM(CASE WHEN card_type LIKE '%VISA%' OR card_type LIKE '%PLATINUM%' THEN 1 ELSE 0 END) as visa_platinum,
                    SUM(CASE WHEN card_type LIKE '%MASTERCARD%' THEN 1 ELSE 0 END) as mastercard,
                    COUNT(DISTINCT form_campaign_id) as unique_campaigns,
                    COUNT(DISTINCT customer_dropped_page) as unique_drop_pages,
                    COUNT(DISTINCT lead_generation_stage) as unique_stages
                FROM mis_data
                WHERE upload_date >= ? AND (
                    form_campaign_id LIKE ? OR uploaded_by = ?
                )
            """, (start_date, f'%{username}%', user_id))
        
        analytics = cursor.fetchone()
        return dict(analytics) if analytics else {}
        
    except Exception as e:
        print(f"Error getting MIS analytics: {e}")
        return {}
    finally:
        conn.close()

def get_user_login_stats(user_id, role, team_leader_id=None, days=30):
    """Get user login statistics including location and time"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        if role == 'admin':
            # Admin sees all users' login stats
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(ll.id) as total_logins,
                    MAX(ll.login_time) as last_login,
                    ll.location,
                    ll.ip_address,
                    ll.user_agent
                FROM users u
                LEFT JOIN login_logs ll ON u.id = ll.user_id
                WHERE ll.login_time >= ? OR ll.login_time IS NULL
                GROUP BY u.id, u.username, ll.location, ll.ip_address, ll.user_agent
                ORDER BY last_login DESC
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader sees team members' login stats
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(ll.id) as total_logins,
                    MAX(ll.login_time) as last_login,
                    ll.location,
                    ll.ip_address,
                    ll.user_agent
                FROM users u
                LEFT JOIN login_logs ll ON u.id = ll.user_id
                WHERE (u.team_leader_id = ? OR u.id = ?) AND (ll.login_time >= ? OR ll.login_time IS NULL)
                GROUP BY u.id, u.username, ll.location, ll.ip_address, ll.user_agent
                ORDER BY last_login DESC
            """, (team_leader_id, user_id, start_date))
            
        else:
            # User sees only their own login stats
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(ll.id) as total_logins,
                    MAX(ll.login_time) as last_login,
                    ll.location,
                    ll.ip_address,
                    ll.user_agent
                FROM users u
                LEFT JOIN login_logs ll ON u.id = ll.user_id
                WHERE u.id = ? AND (ll.login_time >= ? OR ll.login_time IS NULL)
                GROUP BY u.id, u.username, ll.location, ll.ip_address, ll.user_agent
                ORDER BY last_login DESC
            """, (user_id, start_date))
        
        login_stats = cursor.fetchall()
        return [dict(row) for row in login_stats]
        
    except Exception as e:
        print(f"Error getting login stats: {e}")
        return []
    finally:
        conn.close()

def get_lead_analytics_by_status(user_id, role, team_leader_id=None, days=30):
    """Get lead analytics grouped by application status and other key fields"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        if role == 'admin':
            # Admin sees all lead analytics
            cursor.execute("""
                SELECT 
                    application_status,
                    customer_dropped_page,
                    lead_generation_stage,
                    card_type,
                    status,
                    disposition,
                    booking_status,
                    COUNT(*) as count
                FROM mis_data
                WHERE upload_date >= ?
                GROUP BY application_status, customer_dropped_page, lead_generation_stage, card_type, status, disposition, booking_status
                ORDER BY count DESC
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader sees team members' lead analytics
            cursor.execute("""
                SELECT 
                    application_status,
                    customer_dropped_page,
                    lead_generation_stage,
                    card_type,
                    status,
                    disposition,
                    booking_status,
                    COUNT(*) as count
                FROM mis_data
                WHERE upload_date >= ? AND (
                    username IN (SELECT username FROM users WHERE team_leader_id = ?) OR
                    uploaded_by IN (SELECT id FROM users WHERE team_leader_id = ?) OR
                    uploaded_by = ? OR username = ?
                )
                GROUP BY application_status, customer_dropped_page, lead_generation_stage, card_type, status, disposition, booking_status
                ORDER BY count DESC
            """, (start_date, team_leader_id, team_leader_id, user_id, get_username_by_id(user_id)))
            
        else:
            # User sees only their own lead analytics
            username = get_username_by_id(user_id)
            cursor.execute("""
                SELECT 
                    application_status,
                    customer_dropped_page,
                    lead_generation_stage,
                    card_type,
                    status,
                    disposition,
                    booking_status,
                    COUNT(*) as count
                FROM mis_data
                WHERE upload_date >= ? AND (
                    form_campaign_id LIKE ? OR uploaded_by = ?
                )
                GROUP BY application_status, customer_dropped_page, lead_generation_stage, card_type, status, disposition, booking_status
                ORDER BY count DESC
            """, (start_date, f'%{username}%', user_id))
        
        analytics = cursor.fetchall()
        return [dict(row) for row in analytics]
        
    except Exception as e:
        print(f"Error getting lead analytics: {e}")
        return []
    finally:
        conn.close()

def get_team_member_detailed_stats(team_leader_id, days=30):
    """Get detailed statistics for each team member"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        cursor.execute("""
            SELECT 
                u.username,
                u.email,
                u.role,
                COUNT(DISTINCT l.id) as total_leads,
                SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
                SUM(CASE WHEN l.status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_leads,
                SUM(CASE WHEN l.status = 'new' THEN 1 ELSE 0 END) as new_leads,
                COUNT(DISTINCT md.id) as total_mis_records,
                SUM(CASE WHEN md.application_status = 'APPROVED' THEN 1 ELSE 0 END) as approved_applications,
                SUM(CASE WHEN md.application_status = 'PENDING' THEN 1 ELSE 0 END) as pending_applications,
                COUNT(DISTINCT ll.id) as total_logins,
                MAX(ll.login_time) as last_login,
                ll.location as last_location
            FROM users u
            LEFT JOIN leads l ON u.username = l.created_by OR u.id = l.assigned_to
            LEFT JOIN mis_data md ON u.username = md.username OR u.id = md.uploaded_by
            LEFT JOIN login_logs ll ON u.id = ll.user_id
            WHERE u.team_leader_id = ? AND (
                l.created_at >= ? OR l.created_at IS NULL
            ) AND (
                md.upload_date >= ? OR md.upload_date IS NULL
            ) AND (
                ll.login_time >= ? OR ll.login_time IS NULL
            )
            GROUP BY u.id, u.username, u.email, u.role, ll.location
            ORDER BY total_leads DESC, total_mis_records DESC
        """, (team_leader_id, start_date, start_date, start_date))
        
        stats = cursor.fetchall()
        return [dict(row) for row in stats]
        
    except Exception as e:
        print(f"Error getting team member detailed stats: {e}")
        return []
    finally:
        conn.close() 