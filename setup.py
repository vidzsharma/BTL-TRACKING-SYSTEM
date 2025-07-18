#!/usr/bin/env python3
"""
HSBC BTL Tracking Tool Setup Script
This script helps you set up and run the BTL tracking application.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🏦 HSBC BTL Tracking Tool Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "data/mis_uploads",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_database():
    """Check database connection"""
    print("🗄️ Checking database connection...")
    
    try:
        # Try to import and test database connection
        from backend.db import connect_db, init_database, create_admin_user
        
        conn = connect_db()
        if conn:
            print("✅ Database connection successful!")
            conn.close()
            
            # Initialize database
            print("🔧 Initializing database...")
            if init_database():
                print("✅ Database initialized successfully!")
                
                # Create admin user
                print("👤 Creating admin user...")
                if create_admin_user():
                    print("✅ Admin user created successfully!")
                    print("   Username: admin")
                    print("   Password: admin123")
                else:
                    print("⚠️ Admin user already exists or creation failed.")
            else:
                print("❌ Database initialization failed!")
                return False
        else:
            print("❌ Database connection failed!")
            print("Please ensure PostgreSQL is running and configured correctly.")
            return False
            
    except ImportError as e:
        print(f"❌ Error importing database module: {e}")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    return True

def start_application():
    """Start the application"""
    print("🚀 Starting BTL Tracking Tool...")
    print()
    print("The application will be available at:")
    print("   Frontend: http://localhost:8501")
    print("   Backend API: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the application.")
    print()
    
    try:
        # Start the application
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print()
    
    # Create directories
    create_directories()
    
    print()
    
    # Check database
    if not check_database():
        print()
        print("❌ Setup failed! Please check the database configuration.")
        print("Make sure PostgreSQL is running and the connection details are correct.")
        sys.exit(1)
    
    print()
    print("✅ Setup completed successfully!")
    print()
    
    # Ask user if they want to start the application
    response = input("🚀 Do you want to start the application now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print()
        start_application()
    else:
        print()
        print("To start the application later, run:")
        print("   streamlit run app.py")
        print()
        print("Thank you for using HSBC BTL Tracking Tool!")

if __name__ == "__main__":
    main() 