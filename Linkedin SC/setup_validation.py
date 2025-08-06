"""
Setup and validation script for LinkedIn Scraper
Run this before using the scraper to ensure everything is properly configured
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'playwright': 'playwright',
        'pandas': 'pandas', 
        'python-dotenv': 'dotenv',
        'aiohttp': 'aiohttp',
        'aiofiles': 'aiofiles',
        'Pillow': 'PIL'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} is missing")
    
    return missing_packages

def check_environment_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("📋 Please copy .env.example to .env and configure your settings")
        return False
    
    print("✅ .env file found")
    
    # Load and check required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD', 'SEARCH_KEYWORDS']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.strip() == '' or 'your_' in value.lower():
            missing_vars.append(var)
            print(f"❌ {var} not configured")
        else:
            print(f"✅ {var} is configured")
    
    return missing_vars

def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Try to get browser executable path
            browser_path = p.chromium.executable_path
            if browser_path and Path(browser_path).exists():
                print("✅ Playwright Chromium browser is installed")
                return True
            else:
                print("❌ Playwright Chromium browser not installed")
                print("🔧 Run: python -m playwright install chromium")
                return False
    except Exception as e:
        print(f"⚠️  Could not verify Playwright browser installation: {str(e)}")
        print("🔧 Try: python -m playwright install chromium")
        return False

def create_output_directories():
    """Create necessary output directories"""
    dirs = ['output', 'output/images']
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def main():
    """Main setup validation function"""
    print("🚀 LinkedIn Scraper Setup Validation")
    print("=" * 40)
    
    issues = []
    
    # Check Python version
    if not check_python_version():
        issues.append("Python version too old")
    
    print()
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        issues.append(f"Missing packages: {', '.join(missing_packages)}")
        print(f"🔧 Install missing packages: pip install {' '.join(missing_packages)}")
    
    print()
    
    # Check environment file
    missing_env_vars = check_environment_file()
    if missing_env_vars:
        issues.append(f"Environment variables not configured: {', '.join(missing_env_vars)}")
    
    print()
    
    # Check Playwright browsers
    if not check_playwright_browsers():
        issues.append("Playwright browser not installed")
    
    print()
    
    # Create directories
    create_output_directories()
    
    print()
    print("=" * 40)
    
    if issues:
        print("❌ Setup Issues Found:")
        for issue in issues:
            print(f"   • {issue}")
        print()
        print("🔧 Please fix the issues above before running the scraper")
        return False
    else:
        print("✅ All checks passed! You're ready to run the LinkedIn scraper")
        print()
        print("🎯 Next steps:")
        print("   1. Configure your .env file with LinkedIn credentials")
        print("   2. Run: python linkedin_scraper.py")
        print("   3. Or use VS Code Task: Ctrl+Shift+P > Tasks: Run Task > Run LinkedIn Scraper")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
