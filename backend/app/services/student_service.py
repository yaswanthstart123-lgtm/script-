"""
SecureHub — Student Service
Handles student detail CRUD operations.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import StudentDetail
from app.models.user import User
from app.schemas.student import StudentDetailCreate, StudentDetailUpdate, StudentDetailResponse


async def create_student_details(
    data: StudentDetailCreate,
    current_user: User,
    db: AsyncSession,
) -> StudentDetailResponse:
    """
    Create student details for the authenticated user.

    Raises:
        HTTPException 409: If student details already exist for this user.
    """
    # Check if details already exist
    result = await db.execute(
        select(StudentDetail).where(StudentDetail.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student details already exist. Use PUT to update.",
        )

    # Create student detail record
    student_detail = StudentDetail(
        user_id=current_user.id,
        name=data.name,
        department=data.department.value,
        section=data.section.value,
    )

    db.add(student_detail)
    await db.flush()
    await db.refresh(student_detail)

    return StudentDetailResponse.model_validate(student_detail)


async def get_student_details(
    current_user: User,
    db: AsyncSession,
) -> StudentDetailResponse:
    """
    Get student details for the authenticated user.

    Raises:
        HTTPException 404: If student details don't exist.
    """
    result = await db.execute(
        select(StudentDetail).where(StudentDetail.user_id == current_user.id)
    )
    student_detail = result.scalar_one_or_none()

    if student_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student details not found. Please submit your details first.",
        )

    return StudentDetailResponse.model_validate(student_detail)


async def update_student_details(
    data: StudentDetailUpdate,
    current_user: User,
    db: AsyncSession,
) -> StudentDetailResponse:
    """
    Update student details for the authenticated user.

    Raises:
        HTTPException 404: If student details don't exist.
    """
    result = await db.execute(
        select(StudentDetail).where(StudentDetail.user_id == current_user.id)
    )
    student_detail = result.scalar_one_or_none()

    if student_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student details not found. Please submit your details first.",
        )

    # Update only provided fields
    if data.name is not None:
        student_detail.name = data.name
    if data.department is not None:
        student_detail.department = data.department.value
    if data.section is not None:
        student_detail.section = data.section.value

    await db.flush()
    await db.refresh(student_detail)

    return StudentDetailResponse.model_validate(student_detail)
