# Installation Guide

Complete installation instructions for all platforms.

## Quick Install

```bash
chmod +x setup.sh
./setup.sh
```

## Platform-Specific Instructions

### Linux / macOS

#### Method 1: Automated Setup (Recommended)

```bash
./setup.sh
```

#### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Add your OpenAI API key

# 4. Create directories
mkdir -p uploads/audio uploads/reports

# 5. Initialize database
alembic upgrade head

# 6. Run application
python main.py
```

### Windows

#### PowerShell

```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
notepad .env  # Add your OpenAI API key

# 4. Create directories
mkdir uploads\audio
mkdir uploads\reports

# 5. Initialize database
alembic upgrade head

# 6. Run application
python main.py
```

#### Git Bash

```bash
# 1. Create virtual environment
python -m venv venv
source venv/Scripts/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
notepad .env  # Add your OpenAI API key

# 4. Create directories
mkdir -p uploads/audio uploads/reports

# 5. Initialize database
alembic upgrade head

# 6. Run application
python main.py
```

## Docker Installation

### Development

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Production

```bash
docker-compose up --build
```

## Database Setup

### SQLite (Default)

No additional setup required. Database file will be created automatically.

### PostgreSQL (Recommended for Production)

#### Using Docker

```bash
docker run --name postgres-reports \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=reports \
  -p 5432:5432 \
  -d postgres:15
```

#### Configure in .env

```env
DB_ENGINE=postgresql
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports
```

#### Apply Migrations

```bash
alembic upgrade head
```

## Verification

Test the installation:

```bash
# Check API is running
curl http://localhost:8000/health

# Access documentation
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
start http://localhost:8000/docs  # Windows
```

## Troubleshooting

### "No module named 'alembic'"

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenAI API key not found"

Ensure `.env` file contains:
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Database Connection Errors

For SQLite issues, try PostgreSQL:

```bash
# Start PostgreSQL with Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15

# Update .env
# DB_ENGINE=postgresql
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=reports

# Recreate database
rm app.db  # Remove SQLite database
alembic upgrade head
```

### Port Already in Use

Change port in `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## Next Steps

1. Configure OpenAI API key in `.env`
2. Start application: `python main.py`
3. Access API docs: http://localhost:8000/docs
4. Test with sample audio file
