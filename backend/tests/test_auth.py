"""
SecureHub — Authentication Tests
Tests for register, login, me, and logout endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRegister:
    """Tests for POST /api/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """Should register a new user and return token."""
        response = await client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "Strong1234!"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Should reject duplicate email registration."""
        payload = {"email": "dupe@example.com", "password": "Strong1234!"}
        await client.post("/api/auth/register", json=payload)
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        """Should reject weak passwords."""
        response = await client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "short"
        })
        assert response.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """Should reject invalid email format."""
        response = await client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "Strong1234!"
        })
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthLogin:
    """Tests for POST /api/auth/login"""

    async def test_login_success(self, client: AsyncClient):
        """Should login with valid credentials."""
        # First register
        await client.post("/api/auth/register", json={
            "email": "login@example.com",
            "password": "Strong1234!"
        })
        # Then login
        response = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Strong1234!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_wrong_password(self, client: AsyncClient):
        """Should reject wrong password."""
        await client.post("/api/auth/register", json={
            "email": "wrongpw@example.com",
            "password": "Strong1234!"
        })
        response = await client.post("/api/auth/login", json={
            "email": "wrongpw@example.com",
            "password": "WrongPass1!"
        })
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Should reject login for non-existent user."""
        response = await client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "Strong1234!"
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthMe:
    """Tests for GET /api/auth/me"""

    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict):
        """Should return current user profile."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "testuser@example.com"

    async def test_get_me_no_token(self, client: AsyncClient):
        """Should reject request without token."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 403
