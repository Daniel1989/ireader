from celery import shared_task
import os
import django
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set up basic logging configuration
log_file = os.path.join(BASE_DIR, 'tasks.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(module)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configure Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scan.settings')
django.setup()

from knowledge.llm import exact, summary
from knowledge.models import HtmlPage

@shared_task(bind=True)
def parse_html_page(self, page_id):
    try:
        html_page = HtmlPage.objects.get(id=page_id)
        text = exact(html_page.html)
        summary_content = summary(text)
        html_page.text = text
        html_page.summary = summary_content
        html_page.save()
        return True
    except Exception as e:
        raise self.retry(exc=e, countdown=60) 