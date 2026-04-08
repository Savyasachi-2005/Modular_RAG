from typing import List, Dict, Optional, Any
from service.infrastructure.database_service import database_service
from lib.security import security_service
from datetime import datetime
import uuid
import logging


logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users in MongoDB."""

    def __init__(self):
        pass

    async def get_collection(self):
        if database_service.db is None:
            await database_service.connect()
        return database_service.db.users

    async def create_user(self, username: str, hashed_password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user in MongoDB."""
        try:
            collection = await self.get_collection()
            normalized_email = email.strip().lower() if email and email.strip() else None
            
            # Check if username already exists
            existing_user = await collection.find_one({"username": username})
            if existing_user:
                raise ValueError(f"Username '{username}' is already taken")

            # Check if email already exists (only when provided)
            if normalized_email:
                existing_email = await collection.find_one({"email": normalized_email})
                if existing_email:
                    raise ValueError("Email is already registered")
            
            # Generate unique user_id
            user_id = str(uuid.uuid4())
            
            user_data = {
                "user_id": user_id,
                "username": username,
                "hashed_password": hashed_password,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }

            # Do not store empty email values to keep sparse unique index behavior correct.
            if normalized_email:
                user_data["email"] = normalized_email
            
            result = await collection.insert_one(user_data)
            
            # Return user data with proper simple types
            user_data["_id"] = str(result.inserted_id)
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            raise e

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by username."""
        try:
            collection = await self.get_collection()
            user = await collection.find_one({"username": username})
            
            if user:
                user["_id"] = str(user["_id"])
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user {username}: {e}")
            raise e

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by user_id."""
        try:
            collection = await self.get_collection()
            user = await collection.find_one({"user_id": user_id})
            
            if user:
                user["_id"] = str(user["_id"])
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by id {user_id}: {e}")
            raise e

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by email."""
        try:
            if not email:
                return None
                
            collection = await self.get_collection()
            user = await collection.find_one({"email": email})
            
            if user:
                user["_id"] = str(user["_id"])
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise e


    async def update_api_keys(self, user_id: str, api_keys: Dict[str, str]) -> bool:
        """Update user API keys securely."""
        try:
            collection = await self.get_collection()
            
            # Fetch existing user to get current keys (to merge if needed, or just overwrite)
            user = await collection.find_one({"user_id": user_id})
            if not user:
                return False
                
            current_keys = user.get("api_keys", {})
            
            # Encrypt and update keys
            for provider, key in api_keys.items():
                if key: # If key is provided
                    current_keys[provider] = security_service.encrypt_value(key)
                elif provider in current_keys and key == "": 
                    # If empty string provided, remove the key
                    del current_keys[provider]
            
            await collection.update_one(
                {"user_id": user_id},
                {"$set": {"api_keys": current_keys}}
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating API keys for user {user_id}: {e}")
            raise e

    async def get_decrypted_api_keys(self, user_id: str) -> Dict[str, str]:
        """Retrieve decrypted API keys for a user."""
        try:
            collection = await self.get_collection()
            user = await collection.find_one({"user_id": user_id})
            
            if not user or "api_keys" not in user:
                return {}
            
            decrypted_keys = {}
            for provider, encrypted_key in user["api_keys"].items():
                val = security_service.decrypt_value(encrypted_key)
                if val:
                    decrypted_keys[provider] = val
                
            return decrypted_keys
            
        except Exception as e:
            logger.error(f"Error fetching API keys for user {user_id}: {e}")
            return {}

# Singleton instance

user_service = UserService()
