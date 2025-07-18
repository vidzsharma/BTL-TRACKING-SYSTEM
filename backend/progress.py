from backend.db import get_db_cursor, close_db_connection
from datetime import datetime, timedelta
import json

def create_lead(user_id, campaign_tag, customer_name=None, customer_phone=None, customer_email=None, bank_name=None):
    """Create a new lead"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return False, "Database connection failed"
    
    try:
        cursor.execute("""
            INSERT INTO leads 
            (user_id, campaign_tag, customer_name, customer_phone, customer_email, bank_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING lead_id
        """, (user_id, campaign_tag, customer_name, customer_phone, customer_email, bank_name))
        
        lead_id = cursor.fetchone()['lead_id']
        conn.commit()
        
        return True, {"lead_id": lead_id, "message": "Lead created successfully"}
        
    except Exception as e:
        print(f"Error creating lead: {e}")
        conn.rollback()
        return False, f"Error creating lead: {str(e)}"
    finally:
        close_db_connection(conn, cursor)

def update_lead_progress(lead_id, user_id, progress_status, progress_notes=None):
    """Update lead progress"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return False, "Database connection failed"
    
    try:
        # Update lead status
        cursor.execute("""
            UPDATE leads 
            SET lead_status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE lead_id = %s AND user_id = %s
        """, (progress_status, lead_id, user_id))
        
        if cursor.rowcount == 0:
            return False, "Lead not found or access denied"
        
        # Add progress tracking record
        cursor.execute("""
            INSERT INTO progress_tracking 
            (lead_id, user_id, progress_status, progress_notes)
            VALUES (%s, %s, %s, %s)
        """, (lead_id, user_id, progress_status, progress_notes))
        
        conn.commit()
        return True, "Progress updated successfully"
        
    except Exception as e:
        print(f"Error updating lead progress: {e}")
        conn.rollback()
        return False, f"Error updating progress: {str(e)}"
    finally:
        close_db_connection(conn, cursor)

def get_user_leads(user_id, role, team_leader_id=None, status_filter=None):
    """Get leads based on user role"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return []
    
    try:
        if role == 'admin':
            # Admin can see all leads
            query = """
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
            """
            params = []
            
            if status_filter:
                query += " WHERE l.lead_status = %s"
                params.append(status_filter)
            
            query += " ORDER BY l.updated_at DESC"
            
        elif role == 'team_leader':
            # Team leader can see leads of their team members
            query = """
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.user_id IN (
                    SELECT user_id FROM users WHERE team_leader_id = %s
                ) OR l.user_id = %s
            """
            params = [team_leader_id, user_id]
            
            if status_filter:
                query += " AND l.lead_status = %s"
                params.append(status_filter)
            
            query += " ORDER BY l.updated_at DESC"
            
        else:
            # Regular user can only see their own leads
            query = """
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.user_id = %s
            """
            params = [user_id]
            
            if status_filter:
                query += " AND l.lead_status = %s"
                params.append(status_filter)
            
            query += " ORDER BY l.updated_at DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting leads: {e}")
        return []
    finally:
        close_db_connection(conn, cursor)

def get_lead_details(lead_id, user_id, role, team_leader_id=None):
    """Get detailed information about a specific lead"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return None
    
    try:
        if role == 'admin':
            cursor.execute("""
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.lead_id = %s
            """, (lead_id,))
        elif role == 'team_leader':
            cursor.execute("""
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.lead_id = %s AND (
                    l.user_id IN (
                        SELECT user_id FROM users WHERE team_leader_id = %s
                    ) OR l.user_id = %s
                )
            """, (lead_id, team_leader_id, user_id))
        else:
            cursor.execute("""
                SELECT l.*, u.username, u.email as user_email
                FROM leads l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.lead_id = %s AND l.user_id = %s
            """, (lead_id, user_id))
        
        lead = cursor.fetchone()
        
        if lead:
            # Get progress history
            cursor.execute("""
                SELECT pt.*, u.username
                FROM progress_tracking pt
                LEFT JOIN users u ON pt.user_id = u.user_id
                WHERE pt.lead_id = %s
                ORDER BY pt.updated_at DESC
            """, (lead_id,))
            
            progress_history = cursor.fetchall()
            lead = dict(lead)
            lead['progress_history'] = progress_history
        
        return lead
        
    except Exception as e:
        print(f"Error getting lead details: {e}")
        return None
    finally:
        close_db_connection(conn, cursor)

def get_progress_statistics(user_id, role, team_leader_id=None, days=30):
    """Get progress statistics for dashboard"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return {}
    
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        if role == 'admin':
            # Admin statistics
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE assigned_date >= %s
                GROUP BY lead_status
            """, (start_date,))
            
            # Total leads
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE assigned_date >= %s
            """, (start_date,))
            
        elif role == 'team_leader':
            # Team leader statistics
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE assigned_date >= %s AND user_id IN (
                    SELECT user_id FROM users WHERE team_leader_id = %s
                )
                GROUP BY lead_status
            """, (start_date, team_leader_id))
            
            # Total leads
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE assigned_date >= %s AND user_id IN (
                    SELECT user_id FROM users WHERE team_leader_id = %s
                )
            """, (start_date, team_leader_id))
            
        else:
            # User statistics
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE assigned_date >= %s AND user_id = %s
                GROUP BY lead_status
            """, (start_date, user_id))
            
            # Total leads
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE assigned_date >= %s AND user_id = %s
            """, (start_date, user_id))
        
        status_counts = cursor.fetchall()
        total_leads = cursor.fetchone()['total_leads']
        
        # Convert to dictionary
        stats = {
            'total_leads': total_leads,
            'status_breakdown': {}
        }
        
        for status in status_counts:
            stats['status_breakdown'][status['lead_status']] = status['count']
        
        return stats
        
    except Exception as e:
        print(f"Error getting progress statistics: {e}")
        return {}
    finally:
        close_db_connection(conn, cursor)

def get_campaign_progress(campaign_tag, user_id, role, team_leader_id=None):
    """Get progress for specific campaign"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return {}
    
    try:
        if role == 'admin':
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = %s
                GROUP BY lead_status
            """, (campaign_tag,))
            
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE campaign_tag = %s
            """, (campaign_tag,))
            
        elif role == 'team_leader':
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = %s AND user_id IN (
                    SELECT user_id FROM users WHERE team_leader_id = %s
                )
                GROUP BY lead_status
            """, (campaign_tag, team_leader_id))
            
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE campaign_tag = %s AND user_id IN (
                    SELECT user_id FROM users WHERE team_leader_id = %s
                )
            """, (campaign_tag, team_leader_id))
            
        else:
            cursor.execute("""
                SELECT 
                    lead_status,
                    COUNT(*) as count
                FROM leads
                WHERE campaign_tag = %s AND user_id = %s
                GROUP BY lead_status
            """, (campaign_tag, user_id))
            
            cursor.execute("""
                SELECT COUNT(*) as total_leads
                FROM leads
                WHERE campaign_tag = %s AND user_id = %s
            """, (campaign_tag, user_id))
        
        status_counts = cursor.fetchall()
        total_leads = cursor.fetchone()['total_leads']
        
        # Convert to dictionary
        campaign_stats = {
            'campaign_tag': campaign_tag,
            'total_leads': total_leads,
            'status_breakdown': {}
        }
        
        for status in status_counts:
            campaign_stats['status_breakdown'][status['lead_status']] = status['count']
        
        return campaign_stats
        
    except Exception as e:
        print(f"Error getting campaign progress: {e}")
        return {}
    finally:
        close_db_connection(conn, cursor)

def get_user_performance(user_id, role, team_leader_id=None, days=30):
    """Get user performance metrics"""
    conn, cursor = get_db_cursor()
    if not conn or not cursor:
        return {}
    
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        if role == 'admin':
            # Get performance for all users
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.lead_id) as total_leads,
                    COUNT(CASE WHEN l.lead_status = 'closed' THEN 1 END) as closed_leads,
                    COUNT(CASE WHEN l.lead_status = 'in-progress' THEN 1 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.user_id = l.user_id AND l.assigned_date >= %s
                WHERE u.role = 'user'
                GROUP BY u.user_id, u.username
                ORDER BY closed_leads DESC
            """, (start_date,))
            
        elif role == 'team_leader':
            # Get performance for team members
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.lead_id) as total_leads,
                    COUNT(CASE WHEN l.lead_status = 'closed' THEN 1 END) as closed_leads,
                    COUNT(CASE WHEN l.lead_status = 'in-progress' THEN 1 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.user_id = l.user_id AND l.assigned_date >= %s
                WHERE u.team_leader_id = %s
                GROUP BY u.user_id, u.username
                ORDER BY closed_leads DESC
            """, (start_date, team_leader_id))
            
        else:
            # Get performance for individual user
            cursor.execute("""
                SELECT 
                    u.username,
                    COUNT(l.lead_id) as total_leads,
                    COUNT(CASE WHEN l.lead_status = 'closed' THEN 1 END) as closed_leads,
                    COUNT(CASE WHEN l.lead_status = 'in-progress' THEN 1 END) as in_progress_leads
                FROM users u
                LEFT JOIN leads l ON u.user_id = l.user_id AND l.assigned_date >= %s
                WHERE u.user_id = %s
                GROUP BY u.user_id, u.username
            """, (start_date, user_id))
        
        performance_data = cursor.fetchall()
        
        # Calculate success rate
        for user in performance_data:
            user = dict(user)
            if user['total_leads'] > 0:
                user['success_rate'] = round((user['closed_leads'] / user['total_leads']) * 100, 2)
            else:
                user['success_rate'] = 0
        
        return performance_data
        
    except Exception as e:
        print(f"Error getting user performance: {e}")
        return []
    finally:
        close_db_connection(conn, cursor) 