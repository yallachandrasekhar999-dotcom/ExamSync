"""
Alternative seed script using API signup endpoint
"""
import requests
import time

API_BASE = "http://localhost:8000"

def create_users_via_api():
    """Create users by calling the signup API"""
    
    users = [
        {"username": "student", "name": "Alex Student", "password": "123", "role": "student"},
        {"username": "admin", "name": "Super Admin", "password": "123", "role": "admin"},
        {"username": "author", "name": "Dr. Smith", "password": "123", "role": "author"},
    ]
    
    print("Creating users via API...")
    for user in users:
        try:
            response = requests.post(f"{API_BASE}/api/auth/signup", json=user)
            if response.status_code == 200:
                print(f"[OK] Created {user['role']}: {user['username']}")
            else:
                print(f"[FAIL] Failed to create {user['username']}: {response.text}")
        except Exception as e:
            print(f"[ERROR] Error creating {user['username']}: {e}")
    
    print("\nUsers created successfully!")

if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(1)
    create_users_via_api()
