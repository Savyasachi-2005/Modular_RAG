from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from schema.user_schema import UserCreate, UserLogin
from schema.token_schema import Token
from controller.auth_controller import auth_controller
from service.auth_service import get_current_user

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user
    """
    return await auth_controller.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access token
    """
    return await auth_controller.login_for_access_token(user_credentials)

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information (Protected route)
    """
    # Remove sensitive information
    user_info = {
        "username": current_user["username"],
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at"),
        "is_active": current_user.get("is_active", True)
    }
    return {"user": user_info}

@router.get("/health")
async def auth_health_check():
    """
    Health check endpoint for auth service
    """
    return {
        "status": "healthy",
        "service": "auth",
        "message": "Authentication service is operational"
    }