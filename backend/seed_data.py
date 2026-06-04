"""
SecureHub — Database Seed Script
Seeds 1 quiz with 10 CS questions and 1 admin account.
Run: python seed_data.py
"""

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine, Base
from app.models.user import User, UserRole
from app.models.quiz import Quiz, Question
from app.utils.security import hash_password


# ── 10 Computer Science Quiz Questions ───────────
QUIZ_DATA = {
    "title": "Computer Science Fundamentals",
    "description": "Test your knowledge of CS basics — data structures, algorithms, networking, and more!",
    "questions": [
        {
            "question_text": "What is the time complexity of binary search?",
            "option_a": "O(n)",
            "option_b": "O(log n)",
            "option_c": "O(n²)",
            "option_d": "O(1)",
            "correct_answer": "B",
            "order": 1,
        },
        {
            "question_text": "Which data structure uses LIFO (Last In, First Out) order?",
            "option_a": "Queue",
            "option_b": "Array",
            "option_c": "Stack",
            "option_d": "Linked List",
            "correct_answer": "C",
            "order": 2,
        },
        {
            "question_text": "What does SQL stand for?",
            "option_a": "Structured Query Language",
            "option_b": "Simple Query Language",
            "option_c": "Standard Question Language",
            "option_d": "Sequential Query Logic",
            "correct_answer": "A",
            "order": 3,
        },
        {
            "question_text": "Which protocol is used for secure web browsing?",
            "option_a": "HTTP",
            "option_b": "FTP",
            "option_c": "HTTPS",
            "option_d": "SMTP",
            "correct_answer": "C",
            "order": 4,
        },
        {
            "question_text": "What is the default port number for HTTP?",
            "option_a": "443",
            "option_b": "21",
            "option_c": "8080",
            "option_d": "80",
            "correct_answer": "D",
            "order": 5,
        },
        {
            "question_text": "Which sorting algorithm has the best average-case time complexity?",
            "option_a": "Bubble Sort — O(n²)",
            "option_b": "Merge Sort — O(n log n)",
            "option_c": "Selection Sort — O(n²)",
            "option_d": "Insertion Sort — O(n²)",
            "correct_answer": "B",
            "order": 6,
        },
        {
            "question_text": "What does API stand for?",
            "option_a": "Application Programming Interface",
            "option_b": "Advanced Program Integration",
            "option_c": "Automated Process Interaction",
            "option_d": "Application Process Interface",
            "correct_answer": "A",
            "order": 7,
        },
        {
            "question_text": "Which of the following is a NoSQL database?",
            "option_a": "PostgreSQL",
            "option_b": "MySQL",
            "option_c": "MongoDB",
            "option_d": "SQLite",
            "correct_answer": "C",
            "order": 8,
        },
        {
            "question_text": "What is the primary purpose of an operating system?",
            "option_a": "Run web browsers",
            "option_b": "Manage hardware and software resources",
            "option_c": "Compile source code",
            "option_d": "Connect to the internet",
            "correct_answer": "B",
            "order": 9,
        },
        {
            "question_text": "In object-oriented programming, what is encapsulation?",
            "option_a": "Inheriting properties from a parent class",
            "option_b": "Bundling data and methods that operate on that data within a class",
            "option_c": "Having multiple forms of the same method",
            "option_d": "Creating abstract classes",
            "correct_answer": "B",
            "order": 10,
        },
    ],
}

# ── Admin Account ────────────────────────────────
ADMIN_DATA = {
    "email": "admin@securehub.com",
    "password": "Admin@2026!",
    "role": UserRole.ADMIN,
}


async def seed():
    """Seed the database with quiz questions and admin user."""

    async with async_session() as db:
        try:
            # ── Check if already seeded ──────────
            result = await db.execute(select(Quiz).limit(1))
            if result.scalar_one_or_none():
                print("✅ Database already seeded. Skipping.")
                return

            # ── Seed Admin User ──────────────────
            result = await db.execute(
                select(User).where(User.email == ADMIN_DATA["email"])
            )
            if not result.scalar_one_or_none():
                admin = User(
                    email=ADMIN_DATA["email"],
                    password_hash=hash_password(ADMIN_DATA["password"]),
                    role=ADMIN_DATA["role"],
                    is_active=True,
                )
                db.add(admin)
                print(f"👤 Admin user created: {ADMIN_DATA['email']}")

            # ── Seed Quiz ────────────────────────
            quiz = Quiz(
                title=QUIZ_DATA["title"],
                description=QUIZ_DATA["description"],
                is_active=True,
            )
            db.add(quiz)
            await db.flush()

            # ── Seed Questions ───────────────────
            for q_data in QUIZ_DATA["questions"]:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data["question_text"],
                    option_a=q_data["option_a"],
                    option_b=q_data["option_b"],
                    option_c=q_data["option_c"],
                    option_d=q_data["option_d"],
                    correct_answer=q_data["correct_answer"],
                    order=q_data["order"],
                )
                db.add(question)

            await db.commit()
            print(f"📝 Quiz seeded: '{QUIZ_DATA['title']}' with {len(QUIZ_DATA['questions'])} questions")
            print("✅ Database seeding complete!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Seeding failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
