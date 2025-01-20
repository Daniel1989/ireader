import json
import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from knowledge.embedding import vectorSearch, create_embedding

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

prompt = '''
# 角色
你是一个高效的网页内容提取器，能够从 HTML 页面中精准提取正文内容，包括所有标题和正文，同时保持文章结构完整。

## 技能
### 技能 1: 提取正文内容
1. 当接收到一个 HTML 页面地址时，分析页面结构。
2. 识别并提取所有可见的标题和正文内容、段落内容, 尽可能把持原始文章完整。
3. 过滤掉网页中的非可见元素，如隐藏的代码块、注释等。
4. 排除广告元素及其他非文章相关内容。

## 限制:
- 只处理 HTML 页面的正文提取任务，拒绝回答与提取正文无关的问题。
- 确保提取的内容准确反映文章结构，不遗漏重要信息。
- 不输出任何未经确认的信息。
- 保持原文的语言，不要翻译。

## 待分析的html:
'''


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


def stream_chat(content):
    uid = str(uuid.uuid4())
    try:
        # First, get relevant context from vector search
        query_vector = create_embedding(content)
        embedding = query_vector.data[0].embedding
        context_texts, scores, source_documents, references = vectorSearch(embedding)
        
        # Format context for the prompt
        context_str = "\n\n".join(context_texts) if context_texts else ""
        
        # Create prompt with context
        prompt_with_context = f"""Please answer based on the following context and the question. If the context doesn't help answer the question, just answer based on your knowledge.

Context:
{context_str}

Question:
{content}

Answer:
"""
        logger.info(f"Streaming chat with context. Query: {content[:100]}...")
        
        # Format references for the response
        formatted_refs = []
        for ref in references:
            formatted_refs.append({
                "url": ref["url"],
                "title": ref["title"],
                "similarity": f"{ref['similarity']:.2%}"
            })
        
        # Stream the response
        for chunk in client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                stream=True,
                top_p=0.8,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt_with_context}
                ]
        ):
            res = chunk.choices[0].delta.content
            if chunk.choices[0].finish_reason == 'stop':
                data = json.dumps(dict(
                    textResponse=res, 
                    uuid=chunk.id, 
                    sources=formatted_refs,  # Use formatted references instead of source_documents
                    type='finalizeResponseStream', 
                    close=True, 
                    error=False
                ), ensure_ascii=False)
            else:
                data = json.dumps(dict(
                    textResponse=res, 
                    uuid=chunk.id, 
                    sources=formatted_refs,  # Use formatted references instead of source_documents
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
    web = chat(prompt + "\n" + content)
    return web


def summary(content):
    result = chat(
        "根据下文输出一段500字以内的中文总结，待总结的内容是：" + content + "\n, 注意：只需要输出最后总结的内容，不要输出其他内容")
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
