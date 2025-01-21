from celery import shared_task
import os
import django
import logging
from knowledge.llm import exact, summary, chat, llm_create_embedding, translate_text
from knowledge.models import HtmlPage, Tag, Vector, SystemConfig
from knowledge.embedding import updateOrCreateTable, storeVectorResult
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from knowledge.prompts import get_tag_generation_prompt

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

@shared_task(bind=True)
def parse_html_page(self, page_id):
    try:
        html_page = HtmlPage.objects.get(id=page_id)
        # Set status to PROCESSING
        html_page.status = HtmlPage.Status.PROCESSING
        html_page.save()

        # Get original text
        text = exact(html_page.html)
        
        # Get target language from system config
        try:
            config = SystemConfig.objects.get(key="target_language")
            target_language = config.value.get("language", "Chinese")  # Default to Chinese if not specified
            logger.info(f"Translating text to {target_language}")
            
            # Translate text
            translated_text = translate_text(text, target_language)
            html_page.target_language_text = translated_text
            logger.info("Translation completed successfully")
            
        except SystemConfig.DoesNotExist:
            logger.warning("No target language configuration found, skipping translation")
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            # Continue processing even if translation fails
        
        summary_content = summary(text)
        
        # Generate tags
        tags_response = chat(get_tag_generation_prompt(text))
        tags = [tag.strip() for tag in tags_response.split(',')]
        
        # Save everything and set status to FINISH
        html_page.text = text
        html_page.summary = summary_content
        html_page.status = HtmlPage.Status.FINISH
        html_page.save()
        
        # Create tags
        for tag_name in tags:
            Tag.objects.create(
                name=tag_name,
                html_page=html_page
            )

        # Process vectors
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20,
            length_function=len,
            separators=["\n\n", "\n", " ", ".", ",", "\u200b", "\uff0c", "\u3001", "\uff0e", "\u3002", ""]
        )
        
        texts = text_splitter.create_documents([text])
        contents = [text.page_content for text in texts]
        
        vectors = []
        submissions = []
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(llm_create_embedding, text) for text in contents]
            vector_values = [future.result() for future in as_completed(futures)]

            for index, vector in enumerate(vector_values):
                vector_id = uuid.uuid4()
                text_chunk = contents[index]
                embedding = vector.data[0].embedding
                
                # Save to Vector model (simplified)
                Vector.objects.create(
                    html_page=html_page,
                    vector_id=vector_id
                )
                
                # Prepare data for Lance DB
                vector_record = {
                    "id": str(vector_id),
                    "values": embedding,
                    "metadata": {
                        "text": text_chunk,
                        "url": html_page.url,
                        "title": html_page.title,
                        "description": html_page.summary[:200],
                    }
                }
                vectors.append(vector_record)
                submissions.append({
                    "id": str(vector_id),
                    "text": text_chunk,
                    "url": html_page.url,
                    "title": html_page.title,
                    "description": html_page.summary[:200],
                    "vector": embedding
                })

        # Store in Lance DB
        print("##########################")
        print(submissions)
        print("##########################")
        updateOrCreateTable(submissions)

        # Store vector results in chunks
        size = 500
        chunks = [vectors[i * size:(i + 1) * size] for i in range(math.ceil(len(vectors) / size))]
        storeVectorResult(chunks, html_page.url)
        
        return True
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        # Keep status as PROCESSING on retry
        # raise self.retry(exc=e, countdown=60) 


