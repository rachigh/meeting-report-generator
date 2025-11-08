# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-07

### Added
- Audio transcription using OpenAI Whisper API
- Intelligent summarization using GPT-4
- Automatic extraction of meeting topics
- Automatic extraction of decisions made
- Automatic extraction of action items with assignees and deadlines
- PDF report generation
- Markdown report export
- JWT authentication system
- Database support (SQLite and PostgreSQL)
- Docker containerization
- Complete API documentation (Swagger UI)
- Unit tests for core functionality
- RESTful API with 9 endpoints

### API Endpoints
- `POST /reports/generate` - Complete report generation (upload + transcribe + summarize)
- `POST /reports/upload` - Upload audio file
- `POST /reports/{id}/transcribe` - Transcribe uploaded audio
- `POST /reports/{id}/summarize` - Generate summary
- `GET /reports/` - List all reports
- `GET /reports/{id}` - Get specific report
- `GET /reports/{id}/download/pdf` - Download PDF report
- `GET /reports/{id}/download/markdown` - Download Markdown report
- `DELETE /reports/{id}` - Delete report

### Technical
- FastAPI framework
- Async/await architecture
- SQLAlchemy 2.0+ with async support
- Alembic for database migrations
- Pydantic for data validation
- OpenAI API integration
- ReportLab for PDF generation

## [Unreleased]

### Planned Features
- Speaker diarization (identify different speakers)
- Real-time transcription streaming
- Multi-language report translation
- Custom report templates
- Webhook notifications
- Batch processing
- Cloud storage integration (S3, GCS)
- Advanced analytics dashboard

---

[1.0.0]: https://github.com/rachigh/report-generator/releases/tag/v1.0.0
