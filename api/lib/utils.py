import json
from typing import Dict, Optional
from datetime import datetime

# Simple in-memory user database for development
# In production, this would be replaced with a proper database
users_db: Dict[str, Dict] = {}

def get_user(username: str) -> Optional[Dict]:
    """Get user by username"""
    return users_db.get(username)

def create_user(username: str, hashed_password: str, email: Optional[str] = None) -> Dict:
    """Create a new user"""
    user_data = {
        "username": username,
        "hashed_password": hashed_password,
        "email": email,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    users_db[username] = user_data
    return user_data

def user_exists(username: str) -> bool:
    """Check if user exists"""
    return username in users_db

def save_users_to_file(filepath: str = "users.json"):
    """Save users to a JSON file (for persistence)"""
    try:
        with open(filepath, 'w') as f:
            json.dump(users_db, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

def load_users_from_file(filepath: str = "users.json"):
    """Load users from a JSON file"""
    global users_db
    try:
        with open(filepath, 'r') as f:
            users_db = json.load(f)
    except FileNotFoundError:
        print(f"No existing user file found at {filepath}")
    except Exception as e:
        print(f"Error loading users: {e}")

# Load existing users on module import
load_users_from_file()