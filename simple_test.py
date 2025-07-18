import requests
import json

def test_backend():
    """Simple backend test"""
    try:
        # Test login
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        print("Testing login...")
        response = requests.post("http://localhost:5000/api/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            
            if token:
                print(f"Got token: {token[:20]}...")
                
                # Test profile with token
                headers = {'Authorization': f'Bearer {token}'}
                print("\nTesting profile endpoint...")
                profile_response = requests.get("http://localhost:5000/api/profile", headers=headers)
                print(f"Profile response status: {profile_response.status_code}")
                print(f"Profile response: {profile_response.text}")
                
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_backend() 