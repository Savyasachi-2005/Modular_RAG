from datetime import timedelta
from fastapi import HTTPException, status
from schema.user_schema import UserCreate, UserLogin, UserAPIKeysUpdate
from schema.token_schema import Token
from service.infrastructure.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_password_hash
)
from service.infrastructure.user_service import user_service
from service.infrastructure.database_service import DatabaseConnectionError
from lib.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthController:
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """
        Handle user registration
        """
        try:
            username = user_data.username.strip()
            email = user_data.email.strip().lower() if user_data.email and user_data.email.strip() else None

            if len(username) < 3 or len(username) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username must be between 3 and 50 characters"
                )

            if not username.replace('_', '').replace('-', '').isalnum():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username can only contain letters, numbers, underscores, and hyphens"
                )

            # Check if user already exists
            existing_user = await user_service.get_user_by_username(username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )

            if email:
                existing_email = await user_service.get_user_by_email(email)
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            user = await user_service.create_user(
                username=username,
                hashed_password=hashed_password,
                email=email
            )
            
            logger.info(f"User {username} registered successfully")
            
            return {
                "message": "User registered successfully",
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user.get("email")
            }
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error during registration: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
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
            # Authenticate user (awaiting async function)
            user = await authenticate_user(user_credentials.username, user_credentials.password)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": user["user_id"]},
                expires_delta=access_token_expires
            )
            
            logger.info(f"User {user_credentials.username} logged in successfully")
            
            return Token(access_token=access_token, token_type="bearer")
            
        except HTTPException:
            raise
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during login"
            )

    async def update_api_keys(self, user_id: str, api_keys_data: UserAPIKeysUpdate) -> dict:
        """
        Update user API keys
        """
        try:
            success = await user_service.update_api_keys(user_id, api_keys_data.api_keys)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "API keys updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating API keys: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during API key update"
            )


# Singleton instance
auth_controller = AuthController()