#!/bin/bash

# =====================================================
# Meeting Report Generator - Setup Script
# =====================================================
# Automated installation script for Linux and macOS
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

echo ""
echo "======================================"
echo "  Meeting Report Generator Setup"
echo "======================================"
echo ""

# Check Python version
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.11 or higher from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION detected"

# Check if Python version is >= 3.11
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    print_warning "Python 3.11+ is recommended. You have Python $PYTHON_VERSION"
fi

echo ""

# Create virtual environment
print_info "Creating virtual environment..."
python3 -m venv venv
print_success "Virtual environment created"

echo ""

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

echo ""

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded"

echo ""

# Install dependencies
print_info "Installing dependencies (this may take a few minutes)..."
pip install -e . > /dev/null 2>&1
print_success "Dependencies installed"

echo ""

# Create .env file
if [ ! -f .env ]; then
    print_info "Creating environment configuration file..."
    cp .env.example .env
    print_success "Configuration file created (.env)"
    echo ""
    print_warning "IMPORTANT: You must add your OpenAI API key to the .env file"
    echo "           Open .env and set: OPENAI_API_KEY=sk-proj-your-key-here"
    echo "           Get your key at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter to continue..."
else
    print_success "Configuration file already exists (.env)"
    
    # Check if API key is configured
    if grep -q "your_openai_api_key_here" .env 2>/dev/null || ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo ""
        print_warning "Your OpenAI API key may not be configured properly"
        echo "           Please verify your .env file contains: OPENAI_API_KEY=sk-proj-..."
        echo ""
    fi
fi

echo ""

# Create upload directories
print_info "Creating upload directories..."
mkdir -p uploads/audio
mkdir -p uploads/reports
print_success "Upload directories created"

echo ""

# Initialize database
print_info "Initializing database..."
python -m alembic upgrade head > /dev/null 2>&1
print_success "Database initialized"

echo ""
echo "======================================"
echo "  Setup completed successfully! "
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your OpenAI API key:"
echo "   ${YELLOW}nano .env${NC}  (or your preferred editor)"
echo "   Add: OPENAI_API_KEY=sk-proj-your-actual-key"
echo ""
echo "2. Start the application:"
echo "   ${YELLOW}python main.py${NC}"
echo ""
echo "3. Access the API:"
echo "   ${BLUE}http://localhost:8000${NC}"
echo ""
echo "4. View documentation:"
echo "   ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "For more information, see README.md"
echo ""