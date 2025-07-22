#!/usr/bin/env python3
"""
Simple SQLite Database Browser GUI
Uses built-in tkinter library - no external downloads required
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from pathlib import Path

class DatabaseBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("BTL Tracking Database Browser")
        self.root.geometry("1200x800")
        
        # Database connection
        self.conn = None
        self.db_path = "btl_tracking.db"
        
        self.setup_ui()
        self.connect_database()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="BTL Tracking Database Browser", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Database info
        info_frame = ttk.LabelFrame(main_frame, text="Database Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.db_info_label = ttk.Label(info_frame, text="Database: Not connected")
        self.db_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Table selection
        table_frame = ttk.LabelFrame(main_frame, text="Table Selection", padding="10")
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Label(table_frame, text="Select Table:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(table_frame, textvariable=self.table_var, state="readonly")
        self.table_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.table_combo.bind('<<ComboboxSelected>>', self.load_table_data)
        
        # Quick queries
        query_frame = ttk.LabelFrame(table_frame, text="Quick Queries", padding="10")
        query_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(query_frame, text="Show All Tables", 
                  command=self.show_all_tables).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(query_frame, text="Count Records", 
                  command=self.count_records).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(query_frame, text="Show Users", 
                  command=self.show_users).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(query_frame, text="Show MIS Data", 
                  command=self.show_mis_data).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(query_frame, text="Show RPM001 Data", 
                  command=self.show_rpm001_data).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Data display
        data_frame = ttk.LabelFrame(main_frame, text="Data View", padding="10")
        data_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for data display
        self.tree = ttk.Treeview(data_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def connect_database(self):
        """Connect to the database"""
        try:
            if os.path.exists(self.db_path):
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row  # Enable column access by name
                
                # Update database info
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                self.db_info_label.config(text=f"Database: {self.db_path} ({len(tables)} tables)")
                self.status_var.set(f"Connected to database with {len(tables)} tables")
                
                # Populate table dropdown
                table_names = [table[0] for table in tables]
                self.table_combo['values'] = table_names
                if table_names:
                    self.table_combo.set(table_names[0])
                    self.load_table_data()
                    
            else:
                self.db_info_label.config(text=f"Database not found: {self.db_path}")
                self.status_var.set("Database file not found")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.status_var.set("Database connection failed")
    
    def load_table_data(self, event=None):
        """Load data from selected table"""
        if not self.conn:
            return
            
        table_name = self.table_var.get()
        if not table_name:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Clear existing tree
            self.tree.delete(*self.tree.get_children())
            
            # Configure tree columns
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            # Set column headings
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, minwidth=50)
            
            # Load data (limit to first 1000 rows for performance)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            rows = cursor.fetchall()
            
            for row in rows:
                values = [row[col] if row[col] is not None else '' for col in columns]
                self.tree.insert('', 'end', values=values)
            
            self.status_var.set(f"Loaded {len(rows)} rows from {table_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {str(e)}")
            self.status_var.set("Error loading data")
    
    def show_all_tables(self):
        """Show all tables in the database"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Create new window
            table_window = tk.Toplevel(self.root)
            table_window.title("All Tables")
            table_window.geometry("400x300")
            
            # Create treeview
            tree = ttk.Treeview(table_window, columns=('Table Name', 'Row Count'), show='headings')
            tree.heading('Table Name', text='Table Name')
            tree.heading('Row Count', text='Row Count')
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                tree.insert('', 'end', values=(table_name, count))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show tables: {str(e)}")
    
    def count_records(self):
        """Count records in all tables"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            result = "Record Counts:\n\n"
            total = 0
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                result += f"{table_name}: {count:,} records\n"
                total += count
            
            result += f"\nTotal: {total:,} records"
            
            messagebox.showinfo("Record Counts", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to count records: {str(e)}")
    
    def show_users(self):
        """Show all users"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, username, role, team_leader_id FROM users ORDER BY id")
            users = cursor.fetchall()
            
            # Create new window
            user_window = tk.Toplevel(self.root)
            user_window.title("Users")
            user_window.geometry("600x400")
            
            # Create treeview
            tree = ttk.Treeview(user_window, columns=('ID', 'Username', 'Role', 'Team Leader ID'), show='headings')
            tree.heading('ID', text='ID')
            tree.heading('Username', text='Username')
            tree.heading('Role', text='Role')
            tree.heading('Team Leader ID', text='Team Leader ID')
            
            tree.column('ID', width=50)
            tree.column('Username', width=150)
            tree.column('Role', width=100)
            tree.column('Team Leader ID', width=100)
            
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for user in users:
                tree.insert('', 'end', values=user)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show users: {str(e)}")
    
    def show_mis_data(self):
        """Show MIS data summary"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get MIS data summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT username) as unique_users,
                    COUNT(DISTINCT form_campaign_id) as unique_campaigns,
                    MIN(upload_date) as first_upload,
                    MAX(upload_date) as last_upload
                FROM mis_data
            """)
            summary = cursor.fetchone()
            
            # Get top users
            cursor.execute("""
                SELECT username, COUNT(*) as record_count
                FROM mis_data 
                WHERE username != ''
                GROUP BY username 
                ORDER BY record_count DESC 
                LIMIT 10
            """)
            top_users = cursor.fetchall()
            
            result = f"MIS Data Summary:\n\n"
            result += f"Total Records: {summary[0]:,}\n"
            result += f"Unique Users: {summary[1]}\n"
            result += f"Unique Campaigns: {summary[2]}\n"
            result += f"First Upload: {summary[3]}\n"
            result += f"Last Upload: {summary[4]}\n\n"
            
            result += "Top Users by Record Count:\n"
            for user in top_users:
                result += f"  {user[0]}: {user[1]:,} records\n"
            
            messagebox.showinfo("MIS Data Summary", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show MIS data: {str(e)}")
    
    def show_rpm001_data(self):
        """Show data for RPM001 user"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get RPM001 data
            cursor.execute("""
                SELECT 
                    application_number,
                    lead_id,
                    form_campaign_id,
                    application_status,
                    customer_dropped_page,
                    card_type,
                    upload_date
                FROM mis_data 
                WHERE username = 'RPM001'
                ORDER BY upload_date DESC
                LIMIT 50
            """)
            rpm001_data = cursor.fetchall()
            
            if not rpm001_data:
                messagebox.showinfo("RPM001 Data", "No data found for user RPM001")
                return
            
            # Create new window
            rpm_window = tk.Toplevel(self.root)
            rpm_window.title("RPM001 Data")
            rpm_window.geometry("1000x600")
            
            # Create treeview
            columns = ('App Number', 'Lead ID', 'Campaign ID', 'Status', 'Drop Page', 'Card Type', 'Upload Date')
            tree = ttk.Treeview(rpm_window, columns=columns, show='headings')
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for row in rpm001_data:
                tree.insert('', 'end', values=row)
            
            # Add summary
            summary_label = ttk.Label(rpm_window, 
                                    text=f"Showing {len(rpm001_data)} records for RPM001")
            summary_label.pack(pady=(0, 10))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show RPM001 data: {str(e)}")

def main():
    """Main function to run the database browser"""
    root = tk.Tk()
    app = DatabaseBrowser(root)
    root.mainloop()

if __name__ == "__main__":
    main() 