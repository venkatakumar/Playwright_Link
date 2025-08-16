# LinkedIn Executive Search Scraper

A powerful tool to search and extract LinkedIn profiles of executives (CEOs, CTOs, etc.) based on job titles, locations, and other filters.

## 🎯 What It Does

- **Search by Job Title**: CEO, CTO, CFO, Founder, etc.
- **Filter by Location**: Cities, countries, regions
- **Extract Profile Data**: Names, roles, companies, LinkedIn URLs, locations
- **Export Multiple Formats**: CSV, JSON, Excel
- **Smart Categorization**: Automatically categorizes executive titles
- **Predefined Configurations**: Ready-to-use search setups

## 📊 Data Fields Extracted

For each executive profile, the scraper extracts:

- **Name**: Full name of the executive
- **Profile URL**: Direct LinkedIn profile link
- **Current Role**: Job title/position
- **Company**: Current company name
- **Location**: Geographic location
- **Summary**: Brief professional summary (if available)
- **Mutual Connections**: Shared connections (if visible)
- **Title Category**: Auto-categorized (CEO/Founder, CTO, CFO, etc.)
- **Scraped At**: Timestamp of data collection

## 🚀 Quick Start

### Method 1: Use Predefined Configurations

```bash
python executive_search_demo.py
```

Choose from ready-made configurations:
- `uk_tech_ceos`: UK Technology CEOs and Founders  
- `us_ctos`: US Chief Technology Officers
- `europe_fintech_execs`: European Fintech Executives
- `asia_startup_founders`: Asia Pacific Startup Founders

### Method 2: Custom Search

```python
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper

async def search_executives():
    scraper = LinkedInPeopleSearchScraper()
    
    job_titles = ['CEO', 'Chief Executive Officer', 'Founder']
    locations = ['London, United Kingdom', 'Manchester, United Kingdom']
    
    profiles = await scraper.run_executive_search(
        job_titles=job_titles,
        locations=locations,
        max_profiles=50,
        pages_to_scrape=5
    )
    
    return profiles
```

## 📋 Configuration Options

### Executive Title Categories

- **CEO/Founder**: CEO, Chief Executive Officer, Founder, Co-Founder, President
- **CTO/Tech**: CTO, Chief Technology Officer, VP Engineering, Head of Technology
- **CFO/Finance**: CFO, Chief Financial Officer, Finance Director, VP Finance
- **COO/Operations**: COO, Chief Operating Officer, Operations Director
- **CMO/Marketing**: CMO, Chief Marketing Officer, Marketing Director
- **CHRO/HR**: CHRO, Chief Human Resources Officer, HR Director

### Location Regions

- **UK**: London, Manchester, Birmingham, Edinburgh, Bristol, Leeds
- **USA**: San Francisco, New York, Los Angeles, Chicago, Boston, Seattle
- **Europe**: Berlin, Paris, Amsterdam, Stockholm, Zurich, Milan
- **Asia Pacific**: Singapore, Hong Kong, Tokyo, Sydney, Melbourne, Mumbai
- **Middle East**: Dubai, Tel Aviv, Riyadh, Doha

### Industry Keywords

- **Technology**: Software, AI, SaaS, Cloud, Cybersecurity, Fintech
- **Finance**: Banking, Investment, Private Equity, Asset Management
- **Healthcare**: Pharmaceutical, Biotech, Medical Device, Health Tech
- **Consulting**: Management Consulting, Strategy, Advisory
- **Retail/E-commerce**: Retail, E-commerce, Consumer Goods, Fashion

## 🛠️ Setup Requirements

1. **Install Dependencies**:
   ```bash
   pip install playwright pandas python-dotenv openpyxl
   playwright install chromium
   ```

2. **Configure LinkedIn Credentials**:
   Update your `.env` file:
   ```
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   ```

3. **Run the Scraper**:
   ```bash
   python executive_search_demo.py
   ```

## 📈 Output Examples

### CSV Output
```csv
name,profile_url,current_role,company,location,title_category
John Smith,https://linkedin.com/in/johnsmith,CEO,TechCorp Ltd,London UK,CEO/Founder
Jane Doe,https://linkedin.com/in/janedoe,CTO,InnovateTech,San Francisco,CTO
```

### JSON Output
```json
{
  "name": "John Smith",
  "profile_url": "https://linkedin.com/in/johnsmith",
  "current_role": "CEO",
  "company": "TechCorp Ltd",
  "location": "London, United Kingdom",
  "title_category": "CEO/Founder",
  "scraped_at": "2025-08-12T15:30:00"
}
```

## 🎯 Use Cases

### Business Development
- Find potential partners and clients
- Identify decision-makers in target companies
- Build prospect lists for sales outreach

### Recruitment
- Source executive candidates
- Build talent pipelines
- Research executive backgrounds

### Market Research  
- Analyze executive movements
- Study industry leadership trends
- Competitive intelligence

### Investment Research
- Research startup founders
- Analyze management teams
- Due diligence on leadership

## ⚠️ Important Notes

### LinkedIn Terms of Service
- Use responsibly and respect LinkedIn's terms
- Don't scrape excessively or too frequently
- Consider LinkedIn's rate limits
- Use for research and business purposes only

### Technical Considerations
- Handles 2FA authentication automatically
- Includes random delays to avoid detection
- Robust error handling for network issues
- Saves progress to avoid data loss

### Data Quality
- Filters out incomplete profiles
- Validates LinkedIn URLs
- Handles missing data gracefully
- Categorizes job titles automatically

## 🔧 Advanced Usage

### Custom Search Parameters
```python
# Search for CTOs in specific companies
job_titles = ['CTO', 'Chief Technology Officer']
locations = ['San Francisco', 'Seattle']
max_profiles = 100
pages = 10

profiles = await scraper.run_executive_search(
    job_titles, locations, max_profiles, pages
)
```

### Filter by Company Size
```python
# Add company size filtering (requires LinkedIn Premium)
search_config = {
    'job_titles': ['CEO', 'Founder'],
    'locations': ['London'],
    'company_size': 'startup',  # 1-10 employees
    'industry': 'technology'
}
```

## 📁 File Structure

```
Linkedin SC/
├── linkedin_people_search_scraper.py    # Main scraper class
├── people_search_config.py              # Configuration file
├── executive_search_demo.py             # Easy demo script
├── output/                              # Generated data files
│   ├── linkedin_executives.csv
│   ├── linkedin_executives.json
│   └── linkedin_executives.xlsx
└── .env                                # Your credentials
```

## 🎉 Success Tips

1. **Start Small**: Begin with 20-30 profiles to test
2. **Use Specific Titles**: "Chief Executive Officer" vs just "Executive"
3. **Combine Locations**: Use city + country for better results
4. **Check Manually**: Verify LinkedIn search works manually first
5. **Respect Limits**: Don't run too frequently to avoid blocks

Your LinkedIn executive search scraper is ready to help you find and connect with top executives across industries and locations! 🚀
