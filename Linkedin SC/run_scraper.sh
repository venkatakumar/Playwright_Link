#!/bin/bash
# Linux/macOS Shell Script to Run LinkedIn Scraper
# Save as: run_scraper.sh
# Make executable: chmod +x run_scraper.sh

echo "Starting LinkedIn Posts Scraper..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Run the scraper
echo "Running LinkedIn scraper..."
python linkedin_scraper.py

echo ""
echo "Scraping completed!"
echo "Check the 'output' folder for results."
