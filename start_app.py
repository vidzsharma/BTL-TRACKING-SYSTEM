#!/usr/bin/env python3
"""
BTL Tracking Tool Startup Script
Automatically starts both backend and frontend servers
"""

import subprocess
import sys
import time
import os
import threading
import requests

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting backend server...")
    try:
        subprocess.run([sys.executable, "run_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """Start the Streamlit frontend"""
    print("🚀 Starting frontend server...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:5000/api/profile", timeout=2)
        return response.status_code in [401, 200]  # 401 is expected for unauthenticated request
    except:
        return False

def main():
    """Main startup function"""
    print("🏦 HSBC BTL Tracking Tool")
    print("=" * 50)
    
    # Check if backend is already running
    if check_backend_health():
        print("✅ Backend server is already running")
    else:
        print("🔄 Starting backend server...")
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_backend_health():
                print("✅ Backend server is ready!")
                break
            time.sleep(1)
        else:
            print("❌ Backend server failed to start")
            return
    
    # Start frontend
    print("\n🌐 Starting frontend...")
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Application error: {e}") 