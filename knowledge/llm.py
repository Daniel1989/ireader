import json
import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from knowledge.embedding import vectorSearch, create_embedding
from knowledge.prompts import (
    get_html_extraction_prompt,
    get_translation_prompt,
    get_summary_prompt,
    get_chat_context_prompt
)
from knowledge.models import  Conversation, Message


# Set up logging directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging configuration
log_file = os.path.join(LOG_DIR, 'llm.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(module)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.info(f"LLM logging to: {log_file}")

load_dotenv()

api_key = os.environ["SERVERLESS_API_KEY"]

base_url = os.environ["BASE_URL"]
model_name = os.environ["MODEL_NAME"]
# base_url = os.environ["BASE_URL_LOCAL"]
# model_name = os.environ["MODEL_NAME_LOCAL"]


client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

def clearup(html):
    elements_to_remove = [
        'script',
        'style',
        'noscript',
        'iframe',
        'svg',
        'img',
        'audio',
        'video',
        'canvas',
        'map',
        'source',
        'dialog',
        'menu',
        'menuitem',
        'track',
        'object',
        'embed',
        'form',
        'input',
        'button',
        'select',
        'textarea',
        'label',
        'option',
        'optgroup',
        'aside',
        'footer',
        'header',
        'nav',
        'head',
    ]

    attribuites_to_remove = [
        'style',
        'src',
        'alt',
        'title',
        'role',
        'aria-',
        'tabindex',
        'on',
        'data-',
    ]

    soup = BeautifulSoup(html, 'html.parser')
    all_elements = soup.select('*')
    for element in all_elements:
        if element.name.lower() in elements_to_remove:
            element.extract()

        else:
            attributes = element.attrs
            need_remove_attr = []
            for attr, value in attributes.items():
                if any(attr.lower().startswith(item) for item in attribuites_to_remove):
                    need_remove_attr.append(attr)
            for item in need_remove_attr:
                del element[item]
    return soup.prettify()


def chat(content):
    completion = client.chat.completions.create(
        model=model_name,
        temperature=0.7,
        stream=False,
        top_p=0.8,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content


def stream_chat(content, selected_page_ids=None, history=None, conversation=None):
    uid = str(uuid.uuid4())
    try:
        # First, get relevant context from vector search
        query_vector = create_embedding(content)
        embedding = query_vector.data[0].embedding
        
        # Pass selected_page_ids to vectorSearch if provided
        context_texts, scores, source_documents, references = vectorSearch(
            embedding, 
            page_ids=selected_page_ids if selected_page_ids else None
        )
        
        # Format context for the prompt
        context_str = "\n\n".join(context_texts) if context_texts else ""
        
        # Create prompt with context
        prompt_with_context = get_chat_context_prompt(context_str, content)
        
        # Add history to the messages if provided
        history = [{"role": item.role, "content": item.content} for item in history]
        messages = history if len(history) > 0 else [{"role": "system", "content": "You are a helpful assistant."}]
        messages.append({"role": Message.Role.USER, "content": prompt_with_context})
        
        # Format references for the response
        formatted_refs = []
        # Track unique documents by URL
        unique_refs = {}
        
        for ref in references:
            url = ref["url"]
            if url in unique_refs:
                # Update similarity if higher
                if ref["similarity"] > unique_refs[url]["similarity"]:
                    unique_refs[url]["similarity"] = ref["similarity"]
            else:
                unique_refs[url] = {
                    "url": url,
                    "title": ref["title"],
                    "similarity": ref["similarity"],
                    "distance": ref["distance"]
                }
        
        # Convert to list and format similarity scores
        formatted_refs = [
            {**ref, "similarity": f"{ref['similarity']:.2%}"} 
            for ref in unique_refs.values()
        ]
        
        # 创建一个新的message对象，用于保存这次的llm返回的消息
        try:
            message = Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content="",  # 初始化为空字符串，后续流式响应会逐步填充
                references=formatted_refs
            )
        except Conversation.DoesNotExist:
            logger.error("No conversation found to save message")

        # Stream the response
        for chunk in client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                stream=True,
                top_p=0.8,
                max_tokens=2048,
                messages=messages
        ):
            res = chunk.choices[0].delta.content
            if res:  # Only save if there's content in the response
                try:
                    message.content += res
                    message.references = formatted_refs
                    message.save()
                except Message.DoesNotExist:
                    print("Message does not exist")
                    logger.error(f"Error saving streaming message: {str(e)}")
            if chunk.choices[0].finish_reason == 'stop':
                data = json.dumps(dict(
                    textResponse=res, 
                    uuid=chunk.id, 
                    sources=formatted_refs,
                    type='finalizeResponseStream', 
                    close=True, 
                    error=False
                ), ensure_ascii=False)
            else:
                data = json.dumps(dict(
                    textResponse=res, 
                    uuid=chunk.id, 
                    sources=formatted_refs,
                    type='textResponseChunk', 
                    close=False, 
                    error=False
                ), ensure_ascii=False)
            yield f'data: {data}\n\n'
            
    except Exception as e:
        logger.error(f"Error in stream_chat: {str(e)}")
        error_data = json.dumps(dict(
            textResponse="Sorry, an error occurred while processing your request.", 
            uuid=uid, 
            sources=[], 
            type='finalizeResponseStream', 
            close=True, 
            error=True
        ), ensure_ascii=False)
        yield f'data: {error_data}\n\n'


def exact(html):
    content = clearup(html)
    web = chat(get_html_extraction_prompt() + "\n" + content)
    return web


def summary(content):
    result = chat(get_summary_prompt(content))
    return result


# TODO 使用embedding

def llm_create_embedding(text):
    # model_name = os.environ["EMBEDDING_MODEL_NAME"]
    # response = client.embeddings.create(input=[str(text)], model=model_name)
    # return response
    try:
        response = create_embedding(text)
        return response
    except Exception as e:
        logger.error(f"Azure embedding creation failed: {str(e)}")
        raise e


def translate_text(text, target_language):
    try:
        logger.info(f"Starting translation to {target_language}")
        completion = client.chat.completions.create(
            model=model_name,
            temperature=0.7,
            stream=False,
            top_p=0.8,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": get_translation_prompt(text, target_language)}
            ]
        )
        translated_text = completion.choices[0].message.content
        logger.info("Translation completed successfully")
        return translated_text
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise e
