"""
API endpoints for report generation.
"""

import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.report import (
    ReportResponse,
    ReportListResponse,
    TranscriptionResponse,
    SummaryResponse,
    GenerateReportRequest,
    Topic,
    Decision,
    ActionItem
)
from app.services.report import report_service
from app.utils.file_handler import file_handler
from app.schemas.report import ReportCreate

router = APIRouter()


@router.post(
    "/upload",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an audio file"
)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """
    Upload an audio file for processing.
    
    - **file**: Audio file (mp3, wav, m4a, ogg, webm)
    
    Returns the created report with pending status.
    """
    try:
        # Save uploaded file
        file_path, original_filename, file_size = await file_handler.save_upload_file(
            file, subdirectory="audio"
        )
        
        # Create report in database
        report_data = ReportCreate(
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size
        )
        
        report = await report_service.create_report(db, report_data)
        
        return ReportResponse.model_validate(report)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post(
    "/{report_id}/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe an audio file"
)
async def transcribe_audio(
    report_id: int,
    language: str = None,
    db: AsyncSession = Depends(get_db)
) -> TranscriptionResponse:
    """
    Transcribe the audio file of a report.
    
    - **report_id**: ID of the report to transcribe
    - **language**: Optional language hint (e.g., 'en', 'fr', 'es')
    
    Returns the transcription result.
    """
    try:
        report = await report_service.transcribe_report(db, report_id, language)
        
        return TranscriptionResponse(
            report_id=report.id,
            transcription=report.transcription or "",
            language=report.language,
            duration=report.duration
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post(
    "/{report_id}/summarize",
    response_model=SummaryResponse,
    summary="Generate summary for a report"
)
async def generate_summary(
    report_id: int,
    db: AsyncSession = Depends(get_db)
) -> SummaryResponse:
    """
    Generate a summary from the transcription.
    
    - **report_id**: ID of the report to summarize
    
    Returns the structured summary with topics, decisions, and action items.
    """
    try:
        report = await report_service.generate_summary(db, report_id)
        
        # Parse JSON fields
        topics = []
        if report.topics:
            topics_data = json.loads(report.topics)
            topics = [Topic(**t) for t in topics_data]
        
        decisions = []
        if report.decisions:
            decisions_data = json.loads(report.decisions)
            decisions = [Decision(**d) for d in decisions_data]
        
        action_items = []
        if report.action_items:
            action_items_data = json.loads(report.action_items)
            action_items = [ActionItem(**a) for a in action_items_data]
        
        return SummaryResponse(
            report_id=report.id,
            summary=report.summary or "",
            topics=topics,
            decisions=decisions,
            action_items=action_items
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process audio file completely"
)
async def generate_complete_report(
    file: UploadFile = File(..., description="Audio file to process"),
    language: str = None,
    include_summary: bool = True,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """
    Upload an audio file and process it completely (transcription + summary).
    
    - **file**: Audio file (mp3, wav, m4a, ogg, webm)
    - **language**: Optional language hint (e.g., 'en', 'fr', 'es')
    - **include_summary**: Whether to generate summary (default: true)
    
    This is a convenience endpoint that combines upload, transcribe, and summarize.
    """
    try:
        # Save uploaded file
        file_path, original_filename, file_size = await file_handler.save_upload_file(
            file, subdirectory="audio"
        )
        
        # Create report in database
        report_data = ReportCreate(
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size
        )
        
        report = await report_service.create_report(db, report_data)
        
        # Process complete report
        report = await report_service.process_complete_report(
            db, report.id, language, include_summary
        )
        
        return ReportResponse.model_validate(report)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get a report by ID"
)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """
    Get a report by its ID.
    
    - **report_id**: ID of the report
    
    Returns the complete report information.
    """
    report = await report_service.get_report(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return ReportResponse.model_validate(report)


@router.get(
    "/",
    response_model=ReportListResponse,
    summary="List all reports"
)
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> ReportListResponse:
    """
    List all reports with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Returns a list of reports.
    """
    reports = await report_service.list_reports(db, skip, limit)
    
    return ReportListResponse(
        reports=[ReportResponse.model_validate(r) for r in reports],
        total=len(reports)
    )


@router.get(
    "/{report_id}/download/pdf",
    summary="Download report as PDF"
)
async def download_pdf(
    report_id: int,
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Download a report as PDF.
    
    - **report_id**: ID of the report
    
    Returns the PDF file.
    """
    try:
        pdf_path = await report_service.generate_pdf_report(db, report_id)
        
        report = await report_service.get_report(db, report_id)
        filename = f"report_{report_id}_{report.original_filename}.pdf"
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )


@router.get(
    "/{report_id}/download/markdown",
    summary="Download report as Markdown"
)
async def download_markdown(
    report_id: int,
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Download a report as Markdown.
    
    - **report_id**: ID of the report
    
    Returns the Markdown file.
    """
    try:
        md_path = await report_service.generate_markdown_report(db, report_id)
        
        report = await report_service.get_report(db, report_id)
        filename = f"report_{report_id}_{report.original_filename}.md"
        
        return FileResponse(
            path=md_path,
            media_type="text/markdown",
            filename=filename
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Markdown generation failed: {str(e)}"
        )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a report"
)
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a report and its associated files.
    
    - **report_id**: ID of the report to delete
    """
    report = await report_service.get_report(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete associated files
    await file_handler.delete_file(report.file_path)
    
    # Delete PDF and MD if they exist
    pdf_path = file_handler.get_report_path(report_id, "pdf")
    md_path = file_handler.get_report_path(report_id, "md")
    await file_handler.delete_file(pdf_path)
    await file_handler.delete_file(md_path)
    
    # Delete from database
    await db.delete(report)
    await db.commit()
