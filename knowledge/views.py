import asyncio
import math
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
import json

from knowledge.embedding import updateOrCreateTable, storeVectorResult, vectorSearch
# from knowledge.ai_assistants import WeatherAIAssistant
from knowledge.llm import exact, summary, chat, create_embedding, stream_chat
from knowledge.models import HtmlPage, HNIdeas, Conversation, Message
from langchain_text_splitters import RecursiveCharacterTextSplitter

from django.core.paginator import Paginator

import logging
import os

from knowledge.tasks import parse_html_page
from celery.exceptions import OperationalError
from redis.exceptions import ConnectionError, TimeoutError, RedisError
import redis
from django.conf import settings

from knowledge.prompts import (
    get_idea_generation_prompt,
    get_hn_comment_check_prompt,
    get_product_idea_check_prompt
)

# Set up logging directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up basic logging configuration
log_file = os.path.join(LOG_DIR, 'django_views.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(module)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# assistant = WeatherAIAssistant()


# Create your views here.
@csrf_exempt
def create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            title = data.get('title')
            html = data.get('content')
            text = ""
            content = ""
            # Create the object and store the id
            html_page = HtmlPage.objects.create(url=url, title=title, html=html, text=text, summary=content)
            try:
                task = parse_html_page.delay(html_page.id)
            except (OperationalError, ConnectionError, TimeoutError, RedisError) as e:
                return JsonResponse({
                    "success": True, 
                    "message": "创建成功，但后台处理任务暂时无法启动，请稍后重试",
                    "id": html_page.id,
                    "error": str(e)
                })
            except Exception as e:
                return JsonResponse({
                    "success": True,
                    "message": "创建成功，但后台处理任务出现未知错误",
                    "id": html_page.id,
                    "error": str(e)
                })
            
            return JsonResponse({"success": True, "message": "创建成功", "id": html_page.id})
        except Exception as e:
            return JsonResponse({"success": False, "message": "创建失败：" + str(e)})

    return JsonResponse({"success": False, "message": "只支持POST请求"})


def page_list(request):
    page_size = request.GET.get("pageSize", 10)
    page_no = request.GET.get("pageNo", 1)
    pages = HtmlPage.objects.all().order_by('-created')
    p = Paginator(pages, page_size)
    target_page =p.page(page_no)
    data = [{
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "text": item.text,
        "summary": item.summary,
        "created": item.created
    } for item in target_page.object_list]
    return JsonResponse({"success": True, "data": data, "total": p.count, "hasNext": target_page.has_next()})

def generate_idea_from_hn(request):
    # prompt = request.GET.get("prompt")
    article_nums = 50
    keywords = "what are you working on"
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    timestamp = one_year_ago.timestamp()
    url = "http://hn.algolia.com/api/v1/search_by_date?hitsPerPage=" + str(
        article_nums) + "&tags=ask_hn&numericFilters=created_at_i>" + str(
        timestamp) + "&query=" + keywords
    output = requests.get(url)
    output = json.loads(output.text)
    ideas = []
    for item in output["hits"]:
        if "story_text" in item:
            res = chat(get_hn_comment_check_prompt(item["story_text"]))
            if 'Yes' in res:
                url = "https://hn.algolia.com/api/v1/items/" + str(item["story_id"])
                detail_res = requests.get(url)
                detail_res = json.loads(detail_res.text)
                for item in detail_res["children"]:
                    if item["type"] == "comment":
                        comment = gen_comment(item)
                        ideas.append({
                            "story_id": item["story_id"],
                            "comment": comment[0],
                            "commend_id": comment[1],
                            "url": url
                        })
    result = []
    for item in ideas:
        res = chat(get_product_idea_check_prompt(item["comment"]))
        if 'Yes' in res:
            res = chat(get_idea_generation_prompt() + "\n" + item["comment"])
            HNIdeas.objects.create(url=item["url"], story_id=item["story_id"], comment_id=item["commend_id"],
                                summary=res, origin_text=item["comment"])
            result.append(res)
    return JsonResponse({"success": True, "data": result})


def show_ideas(request):
    ideas = HNIdeas.objects.all().order_by('-created')
    data = [item.summary for item in ideas]
    return JsonResponse({"success": True, "data": data})


def gen_comment(comment):
    total = comment["text"]
    commend_id = comment["id"]
    for item in comment["children"]:
        total += "\n" + gen_comment(item)[0]
    return total, commend_id

# Add the custom renderer to the view
@csrf_exempt
def chatgpt(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        response = StreamingHttpResponse(stream_chat(message), content_type="text/event-stream")
        response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
        response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
        return response
    else:
        return JsonResponse({"success": False, "message": "请求方式错误"})

@csrf_exempt
def create_conversation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', f'对话 {timezone_now().strftime("%Y-%m-%d %H:%M")}')
            
            conversation = Conversation.objects.create(title=title)
            
            # Add system message if provided
            initial_message = data.get('message')
            if initial_message:
                Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.USER,
                    content=initial_message
                )
                
                # Get AI response
                response = stream_chat(initial_message)
                Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.ASSISTANT,
                    content=response
                )
            
            return JsonResponse({
                "success": True, 
                "conversation_id": conversation.id,
                "title": conversation.title
            })
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": f"创建对话失败: {str(e)}"
            })
    
    return JsonResponse({"success": False, "message": "只支持POST请求"})

@csrf_exempt
def chat_with_history(request, conversation_id):
    if request.method == 'POST':
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            data = json.loads(request.body)
            message = data.get('message')
            
            # Save user message
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=message
            )
            
            # Get chat history
            history = Message.objects.filter(conversation=conversation).order_by('created')
            history_text = "\n".join([
                f"{'User' if msg.role == Message.Role.USER else 'Assistant'}: {msg.content}"
                for msg in history
            ])
            
            # Stream response with history context
            response = StreamingHttpResponse(
                stream_chat(message, history_text), 
                content_type="text/event-stream"
            )
            response['X-Accel-Buffering'] = 'no'
            response['Cache-Control'] = 'no-cache'
            return response
            
        except Conversation.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "对话不存在"
            })
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": f"聊天失败: {str(e)}"
            })
    
    return JsonResponse({"success": False, "message": "只支持POST请求"})

def get_conversation_history(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.all().order_by('created')
        
        return JsonResponse({
            "success": True,
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "status": conversation.status,
                "messages": [{
                    "role": msg.role,
                    "content": msg.content,
                    "references": msg.references,
                    "created": msg.created.isoformat()
                } for msg in messages]
            }
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "对话不存在"
        })
