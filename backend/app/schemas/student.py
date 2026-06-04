"""
SecureHub — Student Detail Pydantic Schemas
Request/response validation for student profile endpoints.
"""

import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator, ConfigDict


class DepartmentEnum(str, Enum):
    """Department options — matches frontend dropdown exactly."""
    CSE = "CSE"
    IT = "IT"
    ECE = "ECE"
    EEE = "EEE"
    MECH = "MECH"
    CIVIL = "CIVIL"


class SectionEnum(str, Enum):
    """Section options — matches frontend dropdown exactly."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class StudentDetailCreate(BaseModel):
    """Schema for creating student details."""

    name: str
    department: DepartmentEnum
    section: SectionEnum

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Sanitize and validate name input."""
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(v) > 150:
            raise ValueError("Name must not exceed 150 characters")
        # Only allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("Name contains invalid characters")
        return v


class StudentDetailUpdate(BaseModel):
    """Schema for updating student details — all fields optional."""

    name: str | None = None
    department: DepartmentEnum | None = None
    section: SectionEnum | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(v) > 150:
            raise ValueError("Name must not exceed 150 characters")
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("Name contains invalid characters")
        return v


class StudentDetailResponse(BaseModel):
    """Schema for student detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    department: str
    section: str
    created_at: datetime
