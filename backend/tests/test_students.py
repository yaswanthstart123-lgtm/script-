"""
SecureHub — Student Detail Tests
Tests for student detail CRUD endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestStudentDetails:
    """Tests for /api/students/ endpoints"""

    async def test_create_details_success(self, client: AsyncClient, auth_headers: dict):
        """Should create student details."""
        response = await client.post("/api/students/details", json={
            "name": "Tharun Kumar",
            "department": "CSE",
            "section": "A"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tharun Kumar"
        assert data["department"] == "CSE"
        assert data["section"] == "A"

    async def test_create_duplicate_details(self, client: AsyncClient, auth_headers: dict):
        """Should reject duplicate student details."""
        payload = {"name": "Test User", "department": "IT", "section": "B"}
        await client.post("/api/students/details", json=payload, headers=auth_headers)
        response = await client.post("/api/students/details", json=payload, headers=auth_headers)
        assert response.status_code == 409

    async def test_get_details_success(self, client: AsyncClient, auth_headers: dict):
        """Should return student details after creation."""
        await client.post("/api/students/details", json={
            "name": "Test Student",
            "department": "ECE",
            "section": "C"
        }, headers=auth_headers)
        response = await client.get("/api/students/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Student"

    async def test_get_details_not_found(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 if no details exist."""
        response = await client.get("/api/students/me", headers=auth_headers)
        assert response.status_code == 404

    async def test_invalid_department(self, client: AsyncClient, auth_headers: dict):
        """Should reject invalid department."""
        response = await client.post("/api/students/details", json={
            "name": "Bad Dept",
            "department": "INVALID",
            "section": "A"
        }, headers=auth_headers)
        assert response.status_code == 422

    async def test_no_auth(self, client: AsyncClient):
        """Should reject unauthenticated requests."""
        response = await client.post("/api/students/details", json={
            "name": "No Auth",
            "department": "CSE",
            "section": "A"
        })
        assert response.status_code == 403
