"""
SecureHub — Quiz Tests
Tests for quiz listing, questions, submission, and results.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz, Question


@pytest.mark.asyncio
class TestQuiz:
    """Tests for /api/quiz/ endpoints"""

    async def _seed_quiz(self, db_session: AsyncSession) -> int:
        """Helper: seed a quiz with 2 questions."""
        quiz = Quiz(title="Test Quiz", description="A test quiz", is_active=True)
        db_session.add(quiz)
        await db_session.flush()

        q1 = Question(
            quiz_id=quiz.id, question_text="What is 2+2?",
            option_a="3", option_b="4", option_c="5", option_d="6",
            correct_answer="B", order=1,
        )
        q2 = Question(
            quiz_id=quiz.id, question_text="What is Python?",
            option_a="A snake", option_b="A car", option_c="A programming language", option_d="A food",
            correct_answer="C", order=2,
        )
        db_session.add_all([q1, q2])
        await db_session.commit()
        await db_session.refresh(quiz)
        return quiz.id

    async def test_list_quizzes(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Should list active quizzes."""
        await self._seed_quiz(db_session)
        response = await client.get("/api/quiz/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_questions_no_answers(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Should return questions without correct answers."""
        quiz_id = await self._seed_quiz(db_session)
        response = await client.get(f"/api/quiz/{quiz_id}/questions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) == 2
        # Verify correct_answer is NOT exposed
        for q in data["questions"]:
            assert "correct_answer" not in q

    async def test_submit_quiz(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Should submit answers and return graded result."""
        quiz_id = await self._seed_quiz(db_session)

        # Get questions to know IDs
        qr = await client.get(f"/api/quiz/{quiz_id}/questions", headers=auth_headers)
        questions = qr.json()["questions"]

        # Submit correct answers
        answers = {str(questions[0]["id"]): "B", str(questions[1]["id"]): "C"}
        response = await client.post("/api/quiz/submit", json={
            "quiz_id": quiz_id,
            "answers": answers,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 2
        assert data["total_questions"] == 2
        assert data["percentage"] == 100.0

    async def test_get_results(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Should return quiz results after submission."""
        quiz_id = await self._seed_quiz(db_session)
        qr = await client.get(f"/api/quiz/{quiz_id}/questions", headers=auth_headers)
        questions = qr.json()["questions"]
        answers = {str(questions[0]["id"]): "A", str(questions[1]["id"]): "A"}

        await client.post("/api/quiz/submit", json={
            "quiz_id": quiz_id, "answers": answers
        }, headers=auth_headers)

        response = await client.get("/api/quiz/results", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_attempts"] >= 1

    async def test_quiz_not_found(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 for non-existent quiz."""
        response = await client.get("/api/quiz/9999/questions", headers=auth_headers)
        assert response.status_code == 404
