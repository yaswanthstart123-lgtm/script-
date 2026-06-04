"""
SecureHub — Quiz Service
Handles quiz listing, question retrieval, submission, and grading.
Uses Redis caching for frequently accessed quiz data.
"""

import json

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quiz import Quiz, Question, QuizAttempt
from app.models.user import User
from app.schemas.quiz import (
    QuizListResponse, QuizDetailResponse, QuestionResponse,
    QuizSubmit, QuizResultResponse, QuizResultListResponse,
)
from app.redis_client import get_redis


# ── Cache TTL (seconds) ─────────────────────────
QUIZ_CACHE_TTL = 300  # 5 minutes


async def list_quizzes(db: AsyncSession) -> list[QuizListResponse]:
    """List all active quizzes with question counts."""
    result = await db.execute(
        select(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.is_active,
            func.count(Question.id).label("question_count"),
        )
        .outerjoin(Question, Quiz.id == Question.quiz_id)
        .where(Quiz.is_active == True)
        .group_by(Quiz.id)
    )
    rows = result.all()

    return [
        QuizListResponse(
            id=row.id,
            title=row.title,
            description=row.description,
            question_count=row.question_count,
            is_active=row.is_active,
        )
        for row in rows
    ]


async def get_quiz_questions(
    quiz_id: int, db: AsyncSession
) -> QuizDetailResponse:
    """
    Get quiz questions (without correct answers).
    Results are cached in Redis for performance.
    """
    redis = get_redis()

    # ── Try Redis Cache ──────────────────────
    if redis:
        cached = await redis.get(f"quiz:{quiz_id}:questions")
        if cached:
            data = json.loads(cached)
            return QuizDetailResponse(**data)

    # ── Query Database ───────────────────────
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or is inactive",
        )

    # Build response (without correct_answer!)
    questions = [
        QuestionResponse.model_validate(q)
        for q in sorted(quiz.questions, key=lambda x: x.order)
    ]

    response = QuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=questions,
    )

    # ── Cache in Redis ───────────────────────
    if redis:
        await redis.setex(
            f"quiz:{quiz_id}:questions",
            QUIZ_CACHE_TTL,
            json.dumps(response.model_dump(), default=str),
        )

    return response


async def submit_quiz(
    data: QuizSubmit,
    current_user: User,
    db: AsyncSession,
) -> QuizResultResponse:
    """
    Submit quiz answers, grade them, and save the attempt.

    Steps:
    1. Fetch quiz and its questions from DB
    2. Compare submitted answers to correct answers
    3. Calculate score and percentage
    4. Save the attempt record
    5. Return the result
    """
    # Fetch quiz with questions
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == data.quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or is inactive",
        )

    # Build answer key: {question_id: correct_answer}
    answer_key = {str(q.id): q.correct_answer for q in quiz.questions}

    # Grade the answers
    score = 0
    total_questions = len(quiz.questions)

    for question_id, correct_answer in answer_key.items():
        submitted_answer = data.answers.get(question_id, "")
        if submitted_answer.upper() == correct_answer.upper():
            score += 1

    percentage = round((score / total_questions) * 100, 2) if total_questions > 0 else 0.0

    # Save the attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=data.quiz_id,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        answers_json=data.answers,
    )

    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)

    return QuizResultResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=quiz.title,
        score=attempt.score,
        total_questions=attempt.total_questions,
        percentage=attempt.percentage,
        submitted_at=attempt.submitted_at,
    )


async def get_user_results(
    current_user: User,
    db: AsyncSession,
) -> QuizResultListResponse:
    """Get all quiz results for the authenticated user."""
    result = await db.execute(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz))
        .where(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.submitted_at.desc())
    )
    attempts = result.scalars().all()

    results = [
        QuizResultResponse(
            id=a.id,
            quiz_id=a.quiz_id,
            quiz_title=a.quiz.title if a.quiz else None,
            score=a.score,
            total_questions=a.total_questions,
            percentage=a.percentage,
            submitted_at=a.submitted_at,
        )
        for a in attempts
    ]

    return QuizResultListResponse(
        results=results,
        total_attempts=len(results),
    )


async def get_attempt_result(
    attempt_id: int,
    current_user: User,
    db: AsyncSession,
) -> QuizResultResponse:
    """Get a specific quiz attempt result."""
    result = await db.execute(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz))
        .where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == current_user.id,
        )
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found",
        )

    return QuizResultResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz.title if attempt.quiz else None,
        score=attempt.score,
        total_questions=attempt.total_questions,
        percentage=attempt.percentage,
        submitted_at=attempt.submitted_at,
    )
