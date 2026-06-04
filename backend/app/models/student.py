"""
SecureHub — Student Detail ORM Model
Stores student profile information linked to user account.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(str, enum.Enum):
    """Department enumeration — matches frontend dropdown exactly."""
    CSE = "CSE"
    IT = "IT"
    ECE = "ECE"
    EEE = "EEE"
    MECH = "MECH"
    CIVIL = "CIVIL"


class Section(str, enum.Enum):
    """Section enumeration — matches frontend dropdown exactly."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class StudentDetail(Base):
    """Student profile model — one-to-one with User."""

    __tablename__ = "student_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[Department] = mapped_column(
        Enum(Department), nullable=False
    )
    section: Mapped[Section] = mapped_column(
        Enum(Section), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────
    user = relationship("User", back_populates="student_detail")

    def __repr__(self) -> str:
        return f"<StudentDetail(id={self.id}, name='{self.name}', dept='{self.department}')>"
