import sqlite3
import os
from datetime import datetime
from config import Config

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('btl_tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            team_leader_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_location TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (team_leader_id) REFERENCES users (id)
        )
    ''')
    
    # Create mis_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mis_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by INTEGER,
            total_records INTEGER,
            processed_records INTEGER,
            status TEXT DEFAULT 'uploaded',
            file_path TEXT,
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')
    
    # Create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone_number TEXT,
            email TEXT,
            card_type TEXT,
            application_date DATE,
            status TEXT DEFAULT 'new',
            assigned_to INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (assigned_to) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Create progress_tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            leads_contacted INTEGER DEFAULT 0,
            leads_converted INTEGER DEFAULT 0,
            applications_submitted INTEGER DEFAULT 0,
            applications_approved INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create login_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logout_time TIMESTAMP,
            ip_address TEXT,
            location TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_password, 'admin@hsbc.com', 'admin'))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password_hash, email, role='user', team_leader_id=None):
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role, team_leader_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, email, role, team_leader_id))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_login(user_id, location=None):
    """Update user's last login time and location"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET last_login = CURRENT_TIMESTAMP, login_location = ?
        WHERE id = ?
    ''', (location, user_id))
    conn.commit()
    conn.close()

def log_login(user_id, ip_address, location, user_agent):
    """Log user login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO login_logs (user_id, ip_address, location, user_agent)
        VALUES (?, ?, ?, ?)
    ''', (user_id, ip_address, location, user_agent))
    conn.commit()
    conn.close()

def get_team_members(team_leader_id):
    """Get all team members for a team leader"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE team_leader_id = ?', (team_leader_id,))
    members = cursor.fetchall()
    conn.close()
    return members

def get_all_users():
    """Get all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    return users 