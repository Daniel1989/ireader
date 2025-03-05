import logging
from firecrawl import FirecrawlApp
import os
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
load_dotenv()
# Initialize FirecrawlApp
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def fetch_page_content(url):
    """Fetch page content using FirecrawlApp"""
    try:
        scrape_status = app.scrape_url(
            url, 
            params={'formats': ['html']}
        )
        html_content = scrape_status.get('html', '')
        if not html_content:
            return None, "网页内容为空"
            
        return html_content, None
        
    except Exception as e:
        logger.error(f"Error fetching page content: {str(e)}")
        return None, str(e) 