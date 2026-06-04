"""
SecureHub — Quiz Routes
GET  /api/quiz/list                   — List available quizzes
GET  /api/quiz/{quiz_id}/questions    — Get quiz questions (no answers)
POST /api/quiz/submit                 — Submit quiz answers
GET  /api/quiz/results                — Get all results for current user
GET  /api/quiz/results/{attempt_id}   — Get specific attempt result
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.quiz import (
    QuizListResponse, QuizDetailResponse,
    QuizSubmit, QuizResultResponse, QuizResultListResponse,
)
from app.services.quiz_service import (
    list_quizzes,
    get_quiz_questions,
    submit_quiz,
    get_user_results,
    get_attempt_result,
)
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/list",
    response_model=list[QuizListResponse],
    summary="List available quizzes",
    description="Returns all active quizzes with question counts.",
)
async def get_quiz_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all active quizzes."""
    return await list_quizzes(db)


@router.get(
    "/{quiz_id}/questions",
    response_model=QuizDetailResponse,
    summary="Get quiz questions",
    description="Returns all questions for a quiz (correct answers are NOT included).",
)
async def get_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get quiz questions — correct answers are never exposed."""
    return await get_quiz_questions(quiz_id, db)


@router.post(
    "/submit",
    response_model=QuizResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit quiz answers",
    description="Submit answers for a quiz. Returns the graded result with score.",
)
async def submit_answers(
    data: QuizSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit quiz answers and get graded result."""
    return await submit_quiz(data, current_user, db)


@router.get(
    "/results",
    response_model=QuizResultListResponse,
    summary="Get all my quiz results",
    description="Returns all quiz attempt results for the authenticated user.",
)
async def get_my_results(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all quiz results for the current user."""
    return await get_user_results(current_user, db)


@router.get(
    "/results/{attempt_id}",
    response_model=QuizResultResponse,
    summary="Get specific quiz result",
    description="Returns a specific quiz attempt result.",
)
async def get_result(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific quiz attempt result."""
    return await get_attempt_result(attempt_id, current_user, db)
