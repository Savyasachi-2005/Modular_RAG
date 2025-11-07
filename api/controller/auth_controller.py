from datetime import timedelta
from fastapi import HTTPException, status
from schema.user_schema import UserCreate, UserLogin
from schema.token_schema import Token
from service.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_password_hash
)
from lib.utils import create_user, user_exists, save_users_to_file
from lib.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthController:
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """
        Handle user registration
        """
        try:
            # Check if user already exists
            if user_exists(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            user = create_user(
                username=user_data.username,
                hashed_password=hashed_password,
                email=user_data.email
            )
            
            # Save to file for persistence
            save_users_to_file()
            
            logger.info(f"User {user_data.username} registered successfully")
            
            return {
                "message": "User registered successfully",
                "username": user["username"],
                "email": user["email"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during registration"
            )
    
    async def login_for_access_token(self, user_credentials: UserLogin) -> Token:
        """
        Handle user login and token generation
        """
        try:
            # Authenticate user
            user = authenticate_user(user_credentials.username, user_credentials.password)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": user["username"]},
                expires_delta=access_token_expires
            )
            
            logger.info(f"User {user_credentials.username} logged in successfully")
            
            return Token(access_token=access_token, token_type="bearer")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during login"
            )

# Singleton instance
auth_controller = AuthController()