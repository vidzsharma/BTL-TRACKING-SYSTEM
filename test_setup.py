#!/usr/bin/env python3
"""
Test script to verify BTL Tracking Tool setup
"""

import requests
import time
import sys
import os

def test_backend_connection():
    """Test if backend server is running"""
    try:
        response = requests.get("http://localhost:5000/api/profile", timeout=5)
        if response.status_code == 401:  # Expected for unauthenticated request
            print("✅ Backend server is running")
            return True
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_database():
    """Test database connection and initialization"""
    try:
        from backend.db import init_db, get_user_by_username
        
        # Initialize database
        init_db()
        
        # Test admin user creation
        admin_user = get_user_by_username('admin')
        if admin_user:
            print("✅ Database initialized successfully")
            print(f"✅ Admin user created: {admin_user['username']}")
            return True
        else:
            print("❌ Admin user not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_login():
    """Test login functionality"""
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post("http://localhost:5000/api/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ Login functionality working")
                print(f"✅ Access token received: {data['access_token'][:20]}...")
                return data['access_token']
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test authenticated endpoints"""
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Test profile endpoint
        response = requests.get("http://localhost:5000/api/profile", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile endpoint working - User: {data['username']}")
        else:
            print(f"❌ Profile endpoint failed: {response.status_code}")
            return False
        
        # Test users endpoint
        response = requests.get("http://localhost:5000/api/users", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Users endpoint working - Found {len(data['users'])} users")
        else:
            print(f"❌ Users endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Authenticated endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing BTL Tracking Tool Setup")
    print("=" * 50)
    
    # Test database
    print("\n1. Testing Database...")
    if not test_database():
        print("❌ Database test failed. Exiting.")
        return False
    
    # Test backend connection
    print("\n2. Testing Backend Connection...")
    if not test_backend_connection():
        print("❌ Backend connection failed. Exiting.")
        return False
    
    # Test login
    print("\n3. Testing Login...")
    token = test_login()
    if not token:
        print("❌ Login test failed. Exiting.")
        return False
    
    # Test authenticated endpoints
    print("\n4. Testing Authenticated Endpoints...")
    if not test_authenticated_endpoints(token):
        print("❌ Authenticated endpoints test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! BTL Tracking Tool is ready to use.")
    print("\n📋 Next steps:")
    print("1. Open your browser and go to: http://localhost:8501")
    print("2. Login with username: admin, password: admin123")
    print("3. Start using the BTL Tracking Tool!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 