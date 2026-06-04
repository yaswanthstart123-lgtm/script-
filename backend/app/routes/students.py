"""
SecureHub — Student Routes
POST /api/students/details — Submit student details
GET  /api/students/me      — Get current student's details
PUT  /api/students/me      — Update student details
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.student import StudentDetailCreate, StudentDetailUpdate, StudentDetailResponse
from app.services.student_service import (
    create_student_details,
    get_student_details,
    update_student_details,
)
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/details",
    response_model=StudentDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit student details",
    description="Submit name, department, and section for the authenticated user.",
)
async def create_details(
    data: StudentDetailCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create student profile details (name, department, section)."""
    return await create_student_details(data, current_user, db)


@router.get(
    "/me",
    response_model=StudentDetailResponse,
    summary="Get my student details",
    description="Returns the authenticated student's profile details.",
)
async def get_my_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's student details."""
    return await get_student_details(current_user, db)


@router.put(
    "/me",
    response_model=StudentDetailResponse,
    summary="Update my student details",
    description="Update name, department, or section for the authenticated user.",
)
async def update_my_details(
    data: StudentDetailUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's student details."""
    return await update_student_details(data, current_user, db)
