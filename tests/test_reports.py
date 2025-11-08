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


# Note: Full integration tests would require:
# 1. Mock OpenAI API responses
# 2. Test audio files
# 3. Database fixtures
# 
# These would be implemented with pytest fixtures and mocking:
#
# @pytest.fixture
# def mock_openai_transcription(monkeypatch):
#     """Mock OpenAI transcription API."""
#     async def mock_create(*args, **kwargs):
#         return MockTranscriptionResponse(
#             text="This is a test transcription",
#             language="en",
#             duration=60.0
#         )
#     
#     monkeypatch.setattr(
#         "openai.resources.audio.AsyncTranscriptions.create",
#         mock_create
#     )
#
# @pytest.mark.asyncio
# async def test_complete_workflow(mock_openai_transcription, test_audio_file):
#     """Test the complete report generation workflow."""
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         # Upload and process
#         files = {"file": ("meeting.mp3", test_audio_file, "audio/mpeg")}
#         response = await client.post(
#             "/reports/generate",
#             files=files,
#             params={"language": "en", "include_summary": True}
#         )
#         
#         assert response.status_code == status.HTTP_201_CREATED
#         report = response.json()
#         assert report["status"] == "completed"
#         assert report["transcription"] is not None
#         assert report["summary"] is not None
