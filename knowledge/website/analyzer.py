import json
import logging
from ..llm import chat

logger = logging.getLogger(__name__)

def get_page_structure_prompt(html_content):
    """Generate prompt for page structure analysis"""
    return """Analyze this HTML page and identify the best CSS selectors to find news article links.
Focus on finding:
1. The container element that holds all news/article items
2. The specific elements that contain article links
3. The pattern of how article URLs are structured

Return the result in JSON format like this:
{
    "article_list_selector": "main selector for the container of all articles",
    "article_link_selector": "selector for the article links within the container",
    "url_pattern": "any specific pattern noticed in article URLs (e.g., '/article/', '/news/', etc.)"
}

HTML Content:
""" + html_content

def analyze_page_structure(html_content):
    """Analyze page structure using AI"""
    try:
        prompt = get_page_structure_prompt(html_content)
        analysis_result = chat(prompt)
        return json.loads(analysis_result), None
    except json.JSONDecodeError:
        logger.error("Failed to parse AI analysis result as JSON")
        return None, "AI分析结果格式错误"
    except Exception as e:
        logger.error(f"Error in page structure analysis: {str(e)}")
        return None, str(e) 