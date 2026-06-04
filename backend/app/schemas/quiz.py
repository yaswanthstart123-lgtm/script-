"""
SecureHub — Quiz Pydantic Schemas
Request/response validation for quiz endpoints.
"""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, ConfigDict, field_validator


class QuestionResponse(BaseModel):
    """Schema for a quiz question — correct_answer is NEVER exposed."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    order: int


class QuizListResponse(BaseModel):
    """Schema for listing available quizzes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    question_count: int
    is_active: bool


class QuizDetailResponse(BaseModel):
    """Schema for a full quiz with questions (no answers)."""

    id: int
    title: str
    description: str | None
    questions: list[QuestionResponse]


class QuizSubmit(BaseModel):
    """Schema for submitting quiz answers."""

    quiz_id: int
    answers: Dict[str, str]  # {"question_id": "A/B/C/D"}

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate that all answers are A, B, C, or D."""
        valid_options = {"A", "B", "C", "D"}
        for question_id, answer in v.items():
            if not question_id.isdigit():
                raise ValueError(f"Invalid question ID: {question_id}")
            answer_upper = answer.strip().upper()
            if answer_upper not in valid_options:
                raise ValueError(
                    f"Invalid answer '{answer}' for question {question_id}. Must be A, B, C, or D"
                )
            v[question_id] = answer_upper
        return v


class QuizResultResponse(BaseModel):
    """Schema for a quiz result."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    quiz_title: str | None = None
    score: int
    total_questions: int
    percentage: float
    submitted_at: datetime


class QuizResultListResponse(BaseModel):
    """Schema for listing all quiz results."""

    results: list[QuizResultResponse]
    total_attempts: int
