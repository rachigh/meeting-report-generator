"""
Report model for storing meeting transcriptions and summaries.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    """Report model for meeting transcriptions and summaries."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in seconds
    
    # Transcription
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Summary
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    decisions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    action_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="pending"
    )  # pending, transcribing, summarizing, completed, failed
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, filename={self.original_filename}, status={self.status})>"
