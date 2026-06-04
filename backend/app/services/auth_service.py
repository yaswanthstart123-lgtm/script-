"""
SecureHub — Authentication Service
Handles user registration, login, and token management.
"""

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password
from app.utils.jwt_handler import create_access_token, blacklist_token

settings = get_settings()


async def register_user(data: UserRegister, db: AsyncSession) -> TokenResponse:
    """
    Register a new user account.

    Steps:
    1. Check if email already exists
    2. Hash the password with bcrypt
    3. Create user record in PostgreSQL
    4. Generate JWT access token
    5. Return token + user info

    Raises:
        HTTPException 409: If email is already registered
    """
    # Check for existing user
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create new user with hashed password
    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.STUDENT,
        is_active=True,
    )

    db.add(new_user)
    await db.flush()  # Get the auto-generated ID
    await db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(new_user),
    )


async def authenticate_user(data: UserLogin, db: AsyncSession) -> TokenResponse:
    """
    Authenticate a user and return a JWT.

    Steps:
    1. Find user by email
    2. Verify password against bcrypt hash
    3. Check if account is active
    4. Generate JWT access token
    5. Return token + user info

    Raises:
        HTTPException 401: Invalid email or password
        HTTPException 403: Account deactivated
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact support.",
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


async def logout_user(token: str) -> dict:
    """
    Logout user by blacklisting their JWT token in Redis.

    The token will remain blacklisted until its natural expiry time.
    """
    await blacklist_token(token)
    return {"message": "Successfully logged out"}
