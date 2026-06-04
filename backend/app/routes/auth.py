"""
SecureHub — Authentication Routes
POST /api/auth/register  — Register a new user
POST /api/auth/login     — Login and get JWT
GET  /api/auth/me        — Get current user profile
POST /api/auth/logout    — Invalidate JWT (blacklist)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, authenticate_user, logout_user
from app.utils.dependencies import get_current_user, security

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Creates a new user with email and password. Returns JWT token on success.",
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account with email and password."""
    return await register_user(data, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to existing account",
    description="Authenticates user with email/password. Returns JWT token.",
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT access token."""
    return await authenticate_user(data, db)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the authenticated user's profile information.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    summary="Logout and invalidate token",
    description="Blacklists the current JWT token in Redis.",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout by blacklisting the current JWT token."""
    return await logout_user(credentials.credentials)
