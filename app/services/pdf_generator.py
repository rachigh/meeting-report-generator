"""
PDF generation service for meeting reports.
"""

import os
from datetime import datetime
from typing import Optional, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

from app.schemas.report import Topic, Decision, ActionItem


class PDFGeneratorService:
    """Service for generating PDF reports."""

    def __init__(self):
        """Initialize the PDF generator service."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor='#1a1a1a',
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor='#2c3e50',
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor='#34495e',
            spaceAfter=8,
            spaceBefore=8
        ))

    def generate_pdf(
        self,
        output_path: str,
        title: str,
        transcription: Optional[str] = None,
        summary: Optional[str] = None,
        topics: Optional[List[Topic]] = None,
        decisions: Optional[List[Decision]] = None,
        action_items: Optional[List[ActionItem]] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Generate a PDF report.
        
        Args:
            output_path: Path where the PDF will be saved
            title: Report title
            transcription: Meeting transcription
            summary: Meeting summary
            topics: List of topics discussed
            decisions: List of decisions made
            action_items: List of action items
            metadata: Additional metadata (date, duration, etc.)
        
        Returns:
            Path to the generated PDF
        """
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Add title
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add metadata
            if metadata:
                elements.extend(self._add_metadata(metadata))
                elements.append(Spacer(1, 0.3 * inch))
            
            # Add summary section
            if summary:
                elements.extend(self._add_summary_section(summary))
                elements.append(Spacer(1, 0.2 * inch))
            
            # Add topics section
            if topics:
                elements.extend(self._add_topics_section(topics))
                elements.append(Spacer(1, 0.2 * inch))
            
            # Add decisions section
            if decisions:
                elements.extend(self._add_decisions_section(decisions))
                elements.append(Spacer(1, 0.2 * inch))
            
            # Add action items section
            if action_items:
                elements.extend(self._add_action_items_section(action_items))
                elements.append(Spacer(1, 0.2 * inch))
            
            # Add transcription section (on new page)
            if transcription:
                elements.append(PageBreak())
                elements.extend(self._add_transcription_section(transcription))
            
            # Build PDF
            doc.build(elements)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    def _add_metadata(self, metadata: dict) -> List:
        """Add metadata section to the PDF."""
        elements = []
        
        if metadata.get('date'):
            date_text = f"<b>Date:</b> {metadata['date']}"
            elements.append(Paragraph(date_text, self.styles['Normal']))
        
        if metadata.get('duration'):
            duration = metadata['duration']
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_text = f"<b>Duration:</b> {minutes}m {seconds}s"
            elements.append(Paragraph(duration_text, self.styles['Normal']))
        
        if metadata.get('language'):
            lang_text = f"<b>Language:</b> {metadata['language']}"
            elements.append(Paragraph(lang_text, self.styles['Normal']))
        
        return elements

    def _add_summary_section(self, summary: str) -> List:
        """Add summary section to the PDF."""
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Paragraph(summary, self.styles['Normal']))
        return elements

    def _add_topics_section(self, topics: List[Topic]) -> List:
        """Add topics section to the PDF."""
        elements = []
        elements.append(Paragraph("Topics Discussed", self.styles['SectionHeader']))
        
        for i, topic in enumerate(topics, 1):
            topic_title = f"<b>{i}. {topic.title}</b>"
            elements.append(Paragraph(topic_title, self.styles['Normal']))
            if topic.description:
                elements.append(Paragraph(topic.description, self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
        
        return elements

    def _add_decisions_section(self, decisions: List[Decision]) -> List:
        """Add decisions section to the PDF."""
        elements = []
        elements.append(Paragraph("Decisions Made", self.styles['SectionHeader']))
        
        for i, decision in enumerate(decisions, 1):
            decision_text = f"<b>{i}.</b> {decision.description}"
            if decision.responsible:
                decision_text += f" <i>(Responsible: {decision.responsible})</i>"
            elements.append(Paragraph(decision_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
        
        return elements

    def _add_action_items_section(self, action_items: List[ActionItem]) -> List:
        """Add action items section to the PDF."""
        elements = []
        elements.append(Paragraph("Action Items", self.styles['SectionHeader']))
        
        for i, item in enumerate(action_items, 1):
            item_text = f"<b>{i}.</b> {item.task}"
            
            details = []
            if item.assignee:
                details.append(f"Assignee: {item.assignee}")
            if item.deadline:
                details.append(f"Deadline: {item.deadline}")
            if item.priority:
                details.append(f"Priority: {item.priority}")
            
            if details:
                item_text += f" <i>({', '.join(details)})</i>"
            
            elements.append(Paragraph(item_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
        
        return elements

    def _add_transcription_section(self, transcription: str) -> List:
        """Add full transcription section to the PDF."""
        elements = []
        elements.append(Paragraph("Full Transcription", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Split transcription into paragraphs
        paragraphs = transcription.split('\n\n')
        for para in paragraphs:
            if para.strip():
                elements.append(Paragraph(para.strip(), self.styles['Normal']))
                elements.append(Spacer(1, 0.1 * inch))
        
        return elements


# Create a singleton instance
pdf_generator_service = PDFGeneratorService()
