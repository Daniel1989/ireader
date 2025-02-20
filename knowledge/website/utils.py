from urllib.parse import urljoin
from bs4 import BeautifulSoup
from ..models import WebsiteCrawlRule
import logging

logger = logging.getLogger(__name__)

def extract_article_links(html_content, selectors, website_url, limit=20):
    """Extract article links from HTML content using provided selectors"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all article containers using the selectors
    article_containers = soup.select(selectors['article_list_selector'])
    if not article_containers:
        return None, "无法找到文章列表容器"
    
    article_links = []
    # Iterate through each container and find links
    for container in article_containers:
        links = container.select(selectors['article_link_selector'])
        for link in links:
            if len(article_links) >= limit:  # Check limit before adding more
                break
            
            href = link.get('href')
            if href:
                # Make sure we have absolute URLs
                full_url = urljoin(website_url, href)
                # Check if URL matches the pattern (if provided)
                if 'url_pattern' not in selectors or selectors['url_pattern'] in full_url:
                    article_links.append(full_url)
        
        if len(article_links) >= limit:  # Check limit after each container
            break
    
    return article_links, None

def save_crawl_rules(domain, selectors):
    """Save or update website crawl rules"""
    try:
        rules, created = WebsiteCrawlRule.objects.update_or_create(
            domain=domain,
            defaults={
                'article_list_selector': selectors['article_list_selector'],
                'article_link_selector': selectors['article_link_selector'],
                'article_title_selector': 'h1',  # Default
                'article_content_selector': 'article'  # Default
            }
        )
        return rules, created
    except Exception as e:
        logger.error(f"Error saving crawl rules: {str(e)}")
        return None, str(e) 