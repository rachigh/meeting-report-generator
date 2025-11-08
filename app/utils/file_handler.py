"""
File handling utilities for audio uploads and storage.
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException

from app.core.config import settings


class FileHandler:
    """Handler for file upload and storage operations."""

    def __init__(self):
        """Initialize the file handler."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.ensure_upload_dir()

    def ensure_upload_dir(self):
        """Ensure the upload directory exists."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "audio").mkdir(exist_ok=True)
        (self.upload_dir / "reports").mkdir(exist_ok=True)

    def validate_audio_file(self, filename: str) -> bool:
        """
        Validate if the file is an allowed audio format.
        
        Args:
            filename: Name of the file to validate
        
        Returns:
            True if valid, False otherwise
        """
        file_ext = Path(filename).suffix.lower()
        return file_ext in settings.ALLOWED_AUDIO_EXTENSIONS

    async def save_upload_file(
        self, 
        upload_file: UploadFile,
        subdirectory: str = "audio"
    ) -> Tuple[str, str, int]:
        """
        Save an uploaded file to disk.
        
        Args:
            upload_file: The uploaded file
            subdirectory: Subdirectory within upload dir (audio/reports)
        
        Returns:
            Tuple of (file_path, original_filename, file_size)
        
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not self.validate_audio_file(upload_file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Allowed formats: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )
        
        # Generate unique filename
        file_ext = Path(upload_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / subdirectory / unique_filename
        
        # Read file content
        content = await upload_file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return str(file_path), upload_file.filename, file_size

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_path: Path to the file to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_report_path(self, report_id: int, format: str = "pdf") -> str:
        """
        Generate a path for a report file.
        
        Args:
            report_id: ID of the report
            format: Format of the report (pdf/md)
        
        Returns:
            Path to the report file
        """
        filename = f"report_{report_id}.{format}"
        return str(self.upload_dir / "reports" / filename)

    def generate_markdown_report(
        self,
        title: str,
        summary: str = "",
        topics: list = None,
        decisions: list = None,
        action_items: list = None,
        transcription: str = ""
    ) -> str:
        """
        Generate a markdown formatted report.
        
        Args:
            title: Report title
            summary: Meeting summary
            topics: List of topics
            decisions: List of decisions
            action_items: List of action items
            transcription: Full transcription
        
        Returns:
            Markdown formatted string
        """
        md_content = f"# {title}\n\n"
        
        # Summary section
        if summary:
            md_content += "## Executive Summary\n\n"
            md_content += f"{summary}\n\n"
        
        # Topics section
        if topics:
            md_content += "## Topics Discussed\n\n"
            for i, topic in enumerate(topics, 1):
                md_content += f"{i}. **{topic.title}**\n"
                if topic.description:
                    md_content += f"   {topic.description}\n"
                md_content += "\n"
        
        # Decisions section
        if decisions:
            md_content += "## Decisions Made\n\n"
            for i, decision in enumerate(decisions, 1):
                md_content += f"{i}. {decision.description}"
                if decision.responsible:
                    md_content += f" *(Responsible: {decision.responsible})*"
                md_content += "\n"
            md_content += "\n"
        
        # Action items section
        if action_items:
            md_content += "## Action Items\n\n"
            for i, item in enumerate(action_items, 1):
                md_content += f"{i}. {item.task}"
                details = []
                if item.assignee:
                    details.append(f"Assignee: {item.assignee}")
                if item.deadline:
                    details.append(f"Deadline: {item.deadline}")
                if item.priority:
                    details.append(f"Priority: {item.priority}")
                if details:
                    md_content += f" *({', '.join(details)})*"
                md_content += "\n"
            md_content += "\n"
        
        # Transcription section
        if transcription:
            md_content += "## Full Transcription\n\n"
            md_content += f"{transcription}\n"
        
        return md_content


# Create a singleton instance
file_handler = FileHandler()
