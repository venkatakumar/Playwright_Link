"""
LinkedIn People Search Configuration
===================================

Common job titles, locations, and search configurations for executive searches
"""

# Executive Job Titles by Category
EXECUTIVE_TITLES = {
    'ceo_founder': [
        'CEO', 'Chief Executive Officer', 'Founder', 'Co-Founder', 
        'Co-CEO', 'Executive Director', 'Managing Director',
        'President', 'Owner', 'Principal'
    ],
    
    'cto_tech': [
        'CTO', 'Chief Technology Officer', 'Chief Technical Officer',
        'VP Engineering', 'VP Technology', 'Head of Engineering',
        'Head of Technology', 'Technical Director', 'Engineering Director'
    ],
    
    'cfo_finance': [
        'CFO', 'Chief Financial Officer', 'Finance Director',
        'VP Finance', 'Head of Finance', 'Financial Director'
    ],
    
    'coo_operations': [
        'COO', 'Chief Operating Officer', 'Operations Director',
        'VP Operations', 'Head of Operations', 'Managing Director'
    ],
    
    'cmo_marketing': [
        'CMO', 'Chief Marketing Officer', 'Marketing Director',
        'VP Marketing', 'Head of Marketing', 'Brand Director'
    ],
    
    'chro_hr': [
        'CHRO', 'Chief Human Resources Officer', 'HR Director',
        'VP Human Resources', 'Head of HR', 'People Director'
    ],
    
    'cio_it': [
        'CIO', 'Chief Information Officer', 'IT Director',
        'VP Information Technology', 'Head of IT', 'Information Technology Director',
        'VP IT', 'Chief Digital Officer', 'CDO'
    ],
    
    'test_qa': [
        'Test Manager', 'Head of Testing', 'QA Manager', 'Quality Assurance Manager',
        'Testing Director', 'QA Director', 'Head of QA', 'Quality Manager',
        'VP Quality Assurance', 'Chief Quality Officer', 'QA Lead',
        'Testing Lead', 'Software Test Manager', 'Automation Test Manager'
    ]
}

# Major Cities and Regions
LOCATIONS = {
    'uk': [
        'London, United Kingdom', 'Manchester, United Kingdom', 
        'Birmingham, United Kingdom', 'Edinburgh, United Kingdom',
        'Bristol, United Kingdom', 'Leeds, United Kingdom'
    ],
    
    'usa': [
        'San Francisco, California', 'New York, New York', 
        'Los Angeles, California', 'Chicago, Illinois',
        'Boston, Massachusetts', 'Seattle, Washington',
        'Austin, Texas', 'Denver, Colorado'
    ],
    
    'europe': [
        'Berlin, Germany', 'Paris, France', 'Amsterdam, Netherlands',
        'Stockholm, Sweden', 'Zurich, Switzerland', 'Milan, Italy',
        'Madrid, Spain', 'Dublin, Ireland'
    ],
    
    'asia_pacific': [
        'Singapore', 'Hong Kong', 'Tokyo, Japan',
        'Sydney, Australia', 'Melbourne, Australia',
        'Mumbai, India', 'Bangalore, India'
    ],
    
    'middle_east': [
        'Dubai, United Arab Emirates', 'Tel Aviv, Israel',
        'Riyadh, Saudi Arabia', 'Doha, Qatar'
    ]
}

# Industry Keywords (can be combined with titles)
INDUSTRY_KEYWORDS = {
    'technology': [
        'Software', 'Tech', 'Technology', 'AI', 'Machine Learning',
        'SaaS', 'Cloud', 'Cybersecurity', 'Fintech', 'EdTech'
    ],
    
    'finance': [
        'Banking', 'Investment', 'Private Equity', 'Venture Capital',
        'Asset Management', 'Insurance', 'Wealth Management'
    ],
    
    'healthcare': [
        'Healthcare', 'Pharmaceutical', 'Biotech', 'Medical Device',
        'Health Tech', 'Digital Health', 'Life Sciences'
    ],
    
    'consulting': [
        'Management Consulting', 'Strategy Consulting', 'Advisory',
        'Consulting', 'Professional Services'
    ],
    
    'retail_ecommerce': [
        'Retail', 'E-commerce', 'Consumer Goods', 'Fashion',
        'Luxury', 'FMCG', 'Marketplace'
    ]
}

# Company Size Filters (LinkedIn Premium feature)
COMPANY_SIZES = {
    'startup': '1-10 employees',
    'small': '11-50 employees', 
    'medium': '51-200 employees',
    'large': '201-1000 employees',
    'enterprise': '1001-5000 employees',
    'mega': '5001+ employees'
}

# Pre-defined Search Configurations
SEARCH_CONFIGS = {
    'uk_tech_ceos': {
        'job_titles': EXECUTIVE_TITLES['ceo_founder'],
        'locations': LOCATIONS['uk'],
        'keywords': INDUSTRY_KEYWORDS['technology'],
        'description': 'UK Technology CEOs and Founders'
    },
    
    'us_ctos': {
        'job_titles': EXECUTIVE_TITLES['cto_tech'],
        'locations': LOCATIONS['usa'],
        'keywords': INDUSTRY_KEYWORDS['technology'],
        'description': 'US Chief Technology Officers'
    },
    
    'europe_fintech_execs': {
        'job_titles': EXECUTIVE_TITLES['ceo_founder'] + EXECUTIVE_TITLES['cto_tech'],
        'locations': LOCATIONS['europe'],
        'keywords': ['Fintech', 'Financial Technology', 'Digital Banking'],
        'description': 'European Fintech Executives'
    },
    
    'asia_startup_founders': {
        'job_titles': ['Founder', 'Co-Founder', 'CEO', 'Startup CEO'],
        'locations': LOCATIONS['asia_pacific'],
        'keywords': ['Startup', 'Early Stage', 'Seed', 'Series A'],
        'description': 'Asia Pacific Startup Founders'
    },
    
    'global_cfos': {
        'job_titles': EXECUTIVE_TITLES['cfo_finance'],
        'locations': LOCATIONS['usa'] + LOCATIONS['uk'],
        'keywords': INDUSTRY_KEYWORDS['technology'] + ['Finance', 'Accounting'],
        'description': 'Global Chief Financial Officers'
    },
    
    'global_cios': {
        'job_titles': EXECUTIVE_TITLES['cio_it'],
        'locations': LOCATIONS['usa'] + LOCATIONS['europe'],
        'keywords': INDUSTRY_KEYWORDS['technology'] + ['Digital Transformation', 'IT Strategy'],
        'description': 'Global Chief Information Officers'
    },
    
    'global_test_managers': {
        'job_titles': EXECUTIVE_TITLES['test_qa'],
        'locations': LOCATIONS['usa'] + LOCATIONS['uk'] + LOCATIONS['europe'][:3],
        'keywords': ['Testing', 'Quality Assurance', 'QA', 'Automation', 'Software Testing'],
        'description': 'Global Test Managers and QA Leaders'
    }
}

def get_search_config(config_name):
    """Get a predefined search configuration"""
    return SEARCH_CONFIGS.get(config_name, {})

def list_available_configs():
    """List all available search configurations"""
    print("📋 AVAILABLE SEARCH CONFIGURATIONS:")
    print("=" * 50)
    for name, config in SEARCH_CONFIGS.items():
        print(f"🎯 {name}: {config['description']}")
        print(f"   Titles: {len(config['job_titles'])} titles")
        print(f"   Locations: {len(config['locations'])} locations")
        print()

def build_custom_search(title_category, location_region, industry=None):
    """Build a custom search configuration"""
    config = {
        'job_titles': EXECUTIVE_TITLES.get(title_category, []),
        'locations': LOCATIONS.get(location_region, []),
        'keywords': INDUSTRY_KEYWORDS.get(industry, []) if industry else [],
        'description': f'Custom search: {title_category} in {location_region}'
    }
    
    if industry:
        config['description'] += f' ({industry})'
    
    return config

if __name__ == "__main__":
    print("LinkedIn People Search Configuration")
    print("=" * 40)
    
    print("\\n📋 Executive Title Categories:")
    for category, titles in EXECUTIVE_TITLES.items():
        print(f"  {category}: {len(titles)} titles")
    
    print("\\n🌍 Location Regions:")
    for region, locations in LOCATIONS.items():
        print(f"  {region}: {len(locations)} locations")
    
    print("\\n🏢 Industry Keywords:")
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        print(f"  {industry}: {len(keywords)} keywords")
    
    print("\\n")
    list_available_configs()
