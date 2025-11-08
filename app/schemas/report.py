"""
Pydantic schemas for report endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    """Schema for a transcription segment with speaker info."""
    
    speaker: Optional[str] = None
    text: str
    start: Optional[float] = None
    end: Optional[float] = None


class Topic(BaseModel):
    """Schema for a discussed topic."""
    
    title: str
    description: Optional[str] = None


class Decision(BaseModel):
    """Schema for a decision made during the meeting."""
    
    description: str
    responsible: Optional[str] = None


class ActionItem(BaseModel):
    """Schema for an action item from the meeting."""
    
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None


class ReportBase(BaseModel):
    """Base schema for report."""
    
    original_filename: str
    file_size: int


class ReportCreate(ReportBase):
    """Schema for creating a report."""
    
    file_path: str


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""
    
    report_id: int
    transcription: str
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[List[TranscriptionSegment]] = None


class SummaryResponse(BaseModel):
    """Schema for summary response."""
    
    report_id: int
    summary: str
    topics: List[Topic]
    decisions: List[Decision]
    action_items: List[ActionItem]


class ReportResponse(BaseModel):
    """Schema for complete report response."""
    
    id: int
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    transcription: Optional[str] = None
    language: Optional[str] = None
    summary: Optional[str] = None
    topics: Optional[List[Topic]] = None
    decisions: Optional[List[Decision]] = None
    action_items: Optional[List[ActionItem]] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to parse JSON strings from database."""
        import json
        
        # If obj is a dict (already processed), return as is
        if isinstance(obj, dict):
            return super().model_validate(obj)
        
        # Parse JSON strings from database model
        data = {
            "id": obj.id,
            "original_filename": obj.original_filename,
            "file_size": obj.file_size,
            "duration": obj.duration,
            "transcription": obj.transcription,
            "language": obj.language,
            "summary": obj.summary,
            "status": obj.status,
            "error_message": obj.error_message,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        
        # Parse JSON fields
        if obj.topics:
            try:
                topics_data = json.loads(obj.topics) if isinstance(obj.topics, str) else obj.topics
                data["topics"] = [Topic(**t) for t in topics_data]
            except:
                data["topics"] = None
        else:
            data["topics"] = None
        
        if obj.decisions:
            try:
                decisions_data = json.loads(obj.decisions) if isinstance(obj.decisions, str) else obj.decisions
                data["decisions"] = [Decision(**d) for d in decisions_data]
            except:
                data["decisions"] = None
        else:
            data["decisions"] = None
        
        if obj.action_items:
            try:
                action_items_data = json.loads(obj.action_items) if isinstance(obj.action_items, str) else obj.action_items
                data["action_items"] = [ActionItem(**a) for a in action_items_data]
            except:
                data["action_items"] = None
        else:
            data["action_items"] = None
        
        return cls(**data)


class ReportListResponse(BaseModel):
    """Schema for list of reports."""
    
    reports: List[ReportResponse]
    total: int


class GenerateReportRequest(BaseModel):
    """Schema for generating a report from audio."""
    
    include_summary: bool = Field(default=True, description="Whether to generate summary")
    language: Optional[str] = Field(default=None, description="Expected language of the audio")
