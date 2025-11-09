"""
Tests for report endpoints.
"""

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    """Test uploading an invalid file type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try to upload a text file (not allowed)
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = await client.post("/reports/upload", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_nonexistent_report():
    """Test getting a report that doesn't exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_reports_empty():
    """Test listing reports when database is empty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reports" in data
        assert "total" in data
        assert isinstance(data["reports"], list)

