# Windows Batch Script to Run LinkedIn Scraper
# Save as: run_scraper.bat

@echo off
echo Starting LinkedIn Posts Scraper...
echo ================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

:: Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    pause
    exit /b 1
)

:: Run the scraper
echo Running LinkedIn scraper...
python linkedin_scraper.py

echo.
echo Scraping completed!
echo Check the 'output' folder for results.
pause
