"""
SecureHub — Security Utilities
Password hashing with bcrypt and input sanitization.
"""

import re
import html

from passlib.context import CryptContext

# ── Bcrypt Password Hashing ─────────────────────
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Cost factor — balances security vs speed
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    - Strips leading/trailing whitespace
    - Escapes HTML entities
    - Removes potentially dangerous patterns
    """
    if not text:
        return text

    # Strip whitespace
    text = text.strip()

    # Escape HTML entities
    text = html.escape(text, quote=True)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove control characters (except newlines and tabs)
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text
