#  Meeting Report Generator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered meeting transcription and intelligent report generation using OpenAI Whisper and GPT-4.

##  Features

- **Audio Transcription** - Automatic speech-to-text with OpenAI Whisper
- **Intelligent Summarization** - AI-powered analysis with GPT-4
- **Structured Extraction** - Auto-detect topics, decisions, and action items
- **Multi-format Export** - Generate PDF and Markdown reports
- **RESTful API** - 9 production-ready endpoints
- **Docker Support** - Containerized deployment

##  Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Installation
```bash
# Clone repository
git clone https://github.com/rachigh/meeting-report-generator.git
cd report-generator

# Run setup script
chmod +x setup.sh
./setup.sh

# Configure API key
# Edit .env and add: OPENAI_API_KEY=sk-proj-your-key-here

# Launch application
python main.py
```

Access the API at **http://localhost:8000/docs**

##  Usage

### Generate Complete Report
```bash
curl -X POST "http://localhost:8000/reports/generate" \
  -F "file=@meeting.mp3" \
  -F "language=en"
```

### Download Reports
```bash
# PDF
curl "http://localhost:8000/reports/1/download/pdf" -o report.pdf

# Markdown
curl "http://localhost:8000/reports/1/download/markdown" -o report.md
```

### Python Example
```python
import requests

# Generate report
with open("meeting.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/reports/generate",
        files={"file": f},
        params={"language": "en"}
    )

report = response.json()
print(f"Summary: {report['summary']}")
```

##  Architecture
```
report-generator/
├── app/
│   ├── api/              # API endpoints
│   ├── services/         # Business logic (Whisper, GPT-4, PDF)
│   ├── models/           # Database models
│   └── schemas/          # Pydantic validation
├── tests/                # Unit tests
├── uploads/              # File storage
└── main.py              # Entry point
```

##  Tech Stack

- **FastAPI** - Modern async web framework
- **OpenAI** - Whisper (transcription) & GPT-4 (summarization)
- **SQLAlchemy** - Async ORM with Alembic migrations
- **ReportLab** - PDF generation
- **Docker** - Containerization

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reports/generate` | POST | Upload audio + generate report |
| `/reports/{id}/download/pdf` | GET | Download PDF report |
| `/reports/{id}/download/markdown` | GET | Download Markdown report |
| `/reports/` | GET | List all reports |
| `/reports/{id}` | GET | Get specific report |
| `/reports/{id}` | DELETE | Delete report |

Full API documentation: http://localhost:8000/docs

##  Configuration

Create `.env` file:
```env
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional
DB_ENGINE=sqlite              # or postgresql
DEBUG=true
MAX_UPLOAD_SIZE=52428800     # 50MB
```

**Supported audio formats:** MP3, WAV, M4A, OGG, WebM  
**Supported languages:** 99+ languages (English, French, Spanish, German, etc.)

##  Docker Deployment
```bash
docker-compose up --build
```

##  Testing
```bash
pytest tests/
```

##  License

MIT License - see [LICENSE](LICENSE) file.

##  Acknowledgments

- [OpenAI Whisper](https://openai.com/research/whisper) - Transcription
- [OpenAI GPT-4](https://openai.com/gpt-4) - Summarization
- [FastAPI](https://fastapi.tiangolo.com/) - Framework

---

**Built with FastAPI and OpenAI APIs**