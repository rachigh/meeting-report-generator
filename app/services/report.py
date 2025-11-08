"""
Report service for managing report generation workflow.
"""

import json
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.schemas.report import (
    ReportCreate, 
    ReportResponse, 
    Topic, 
    Decision, 
    ActionItem
)
from app.services.transcription import transcription_service
from app.services.summary import summary_service
from app.services.pdf_generator import pdf_generator_service
from app.utils.file_handler import file_handler


class ReportService:
    """Service for managing report generation workflow."""

    async def create_report(
        self,
        db: AsyncSession,
        report_data: ReportCreate
    ) -> Report:
        """
        Create a new report in the database.
        
        Args:
            db: Database session
            report_data: Report creation data
        
        Returns:
            Created report
        """
        report = Report(
            original_filename=report_data.original_filename,
            file_path=report_data.file_path,
            file_size=report_data.file_size,
            status="pending"
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return report

    async def get_report(
        self,
        db: AsyncSession,
        report_id: int
    ) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            db: Database session
            report_id: Report ID
        
        Returns:
            Report if found, None otherwise
        """
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """
        List all reports.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of reports
        """
        result = await db.execute(
            select(Report)
            .order_by(Report.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def transcribe_report(
        self,
        db: AsyncSession,
        report_id: int,
        language: Optional[str] = None
    ) -> Report:
        """
        Transcribe the audio file of a report.
        
        Args:
            db: Database session
            report_id: Report ID
            language: Optional language hint
        
        Returns:
            Updated report with transcription
        """
        # Get report
        report = await self.get_report(db, report_id)
        if not report:
            raise ValueError("Report not found")
        
        try:
            # Update status
            report.status = "transcribing"
            await db.commit()
            
            # Transcribe audio
            transcription_result = await transcription_service.transcribe_audio(
                file_path=report.file_path,
                language=language
            )
            
            # Update report
            report.transcription = transcription_result["transcription"]
            report.language = transcription_result.get("language")
            report.duration = transcription_result.get("duration")
            report.status = "transcribed"
            report.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(report)
            
            return report
        
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)
            await db.commit()
            raise

    async def generate_summary(
        self,
        db: AsyncSession,
        report_id: int
    ) -> Report:
        """
        Generate summary for a transcribed report.
        
        Args:
            db: Database session
            report_id: Report ID
        
        Returns:
            Updated report with summary
        """
        # Get report
        report = await self.get_report(db, report_id)
        if not report:
            raise ValueError("Report not found")
        
        if not report.transcription:
            raise ValueError("Report must be transcribed first")
        
        try:
            # Update status
            report.status = "summarizing"
            await db.commit()
            
            # Generate summary
            summary_result = await summary_service.generate_summary(
                transcription=report.transcription
            )
            
            # Update report
            report.summary = summary_result["summary"]
            report.topics = json.dumps([t.model_dump() for t in summary_result["topics"]])
            report.decisions = json.dumps([d.model_dump() for d in summary_result["decisions"]])
            report.action_items = json.dumps([a.model_dump() for a in summary_result["action_items"]])
            report.status = "completed"
            report.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(report)
            
            return report
        
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)
            await db.commit()
            raise

    async def process_complete_report(
        self,
        db: AsyncSession,
        report_id: int,
        language: Optional[str] = None,
        include_summary: bool = True
    ) -> Report:
        """
        Process a complete report: transcription + summary.
        
        Args:
            db: Database session
            report_id: Report ID
            language: Optional language hint
            include_summary: Whether to generate summary
        
        Returns:
            Fully processed report
        """
        # Transcribe
        report = await self.transcribe_report(db, report_id, language)
        
        # Generate summary if requested
        if include_summary:
            report = await self.generate_summary(db, report_id)
        
        return report

    async def generate_pdf_report(
        self,
        db: AsyncSession,
        report_id: int
    ) -> str:
        """
        Generate a PDF report.
        
        Args:
            db: Database session
            report_id: Report ID
        
        Returns:
            Path to the generated PDF
        """
        # Get report
        report = await self.get_report(db, report_id)
        if not report:
            raise ValueError("Report not found")
        
        # Parse JSON fields
        topics = None
        if report.topics:
            topics_data = json.loads(report.topics)
            topics = [Topic(**t) for t in topics_data]
        
        decisions = None
        if report.decisions:
            decisions_data = json.loads(report.decisions)
            decisions = [Decision(**d) for d in decisions_data]
        
        action_items = None
        if report.action_items:
            action_items_data = json.loads(report.action_items)
            action_items = [ActionItem(**a) for a in action_items_data]
        
        # Generate PDF
        pdf_path = file_handler.get_report_path(report_id, "pdf")
        
        metadata = {
            "date": report.created_at.strftime("%Y-%m-%d %H:%M"),
            "duration": report.duration,
            "language": report.language
        }
        
        pdf_generator_service.generate_pdf(
            output_path=pdf_path,
            title=f"Meeting Report - {report.original_filename}",
            transcription=report.transcription,
            summary=report.summary,
            topics=topics,
            decisions=decisions,
            action_items=action_items,
            metadata=metadata
        )
        
        return pdf_path

    async def generate_markdown_report(
        self,
        db: AsyncSession,
        report_id: int
    ) -> str:
        """
        Generate a Markdown report.
        
        Args:
            db: Database session
            report_id: Report ID
        
        Returns:
            Path to the generated Markdown file
        """
        # Get report
        report = await self.get_report(db, report_id)
        if not report:
            raise ValueError("Report not found")
        
        # Parse JSON fields
        topics = None
        if report.topics:
            topics_data = json.loads(report.topics)
            topics = [Topic(**t) for t in topics_data]
        
        decisions = None
        if report.decisions:
            decisions_data = json.loads(report.decisions)
            decisions = [Decision(**d) for d in decisions_data]
        
        action_items = None
        if report.action_items:
            action_items_data = json.loads(report.action_items)
            action_items = [ActionItem(**a) for a in action_items_data]
        
        # Generate Markdown
        md_content = file_handler.generate_markdown_report(
            title=f"Meeting Report - {report.original_filename}",
            summary=report.summary or "",
            topics=topics,
            decisions=decisions,
            action_items=action_items,
            transcription=report.transcription or ""
        )
        
        # Save to file
        md_path = file_handler.get_report_path(report_id, "md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return md_path


# Create a singleton instance
report_service = ReportService()
