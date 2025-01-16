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
from knowledge.models import HtmlPage, HNIdeas
from langchain_text_splitters import RecursiveCharacterTextSplitter

from django.core.paginator import Paginator

import logging

logger = logging.getLogger(__name__)

# assistant = WeatherAIAssistant()

VECTOR_NAMESPACE = 'urlKnowledgeForVec'

prompt = '''
# 角色
你是一个专业且富有洞察力的产品经理，你正在和一个工程师进行对话。对话内容是有关最近他正在做什么的描述，你能够精准地根据他的描述提取出具有创新性和市场潜力的产品，并明确其面向的场景和人群。

## 技能
### 技能 1: 提取产品
1. 仔细分析给定的描述，提取出核心的产品概念和特点。
2. 考虑产品的功能、用途、形态等方面，形成清晰的产品定义。

### 技能 2: 确定面向人群
1. 基于产品的特点和用途，分析可能受益或对其感兴趣的人群特征。
2. 明确人群的年龄范围、性别、职业、消费习惯等关键因素。

## 限制:
- 只依据给定的描述进行产品提取和人群分析，不自行假设或添加额外信息。
- 输出内容应清晰、准确、有条理，符合产品管理的专业规范。

## 对话内容
'''


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
            HtmlPage.objects.create(url=url, title=title, html=html, text=text, summary=content)
        except Exception as e:
            return JsonResponse({"success": False, "message": "创建失败：" + str(e)})

    return JsonResponse({"success": True, "message": "创建成功"})


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


@csrf_exempt
def parse(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        item = HtmlPage.objects.filter(id=id)[0]
        start_time = time.time()
        text = exact(item.html)
        print("parse time:", time.time() - start_time)
        summary_content = summary(text)
        print("total time:", time.time() - start_time)
        item.text = text
        item.summary = summary_content
        item.save()
    return JsonResponse({"success": True})


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
            res = chat(
                "You are a Hacker news reader bot. Check the following story if is asking for people to show their recent ideas. just return 'Yes' or 'No'.\n the story is:\n" +
                item["story_text"])
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
        res = chat(
            "You are a Hacker news reader bot. Check the following comment if is describing a product or an idea about hardware or software or applications. just return 'Yes' or 'No'.\n the comment is:\n" +
            item["comment"])
        if 'Yes' in res:
            res = chat(prompt + "\n" + item["comment"])
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


def create_vector(request):
    # TODO 1122, 这里每次请求进来时，首先要走原来的create，将内容落库
    # 然后启动一个异步任务，进行大模型抓取和向量化
    # 所以需要一个异步轮训，每分钟查找未翻译的，然后进行翻译
    url = 'http://localhost:4321/blog/2024-11-01'
    title = 'Marketing Management Book Summary'
    desc = "Marketing Management Book Summary' Description"

    content = requests.get(url)
    content = content.text
    text = exact(content)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # should less model limit
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],
    )
    texts = text_splitter.create_documents([text])
    contents = [text.page_content for text in texts]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_embedding, text) for text in contents]
        vectorValues = [future.result() for future in as_completed(futures)]

        documentVectors = []
        vectors = []
        submissions = []

        for index, vector in enumerate(vectorValues):
            uid = str(uuid.uuid4())
            text = contents[index]
            embedding = vector.data[0].embedding
            vectorRecord = {
                "id": uid,
                "values": embedding,
                "metadata": {
                    "text": text,
                    "url": url,
                    "title": title,
                    "description": desc,
                }
            }
            vectors.append(vectorRecord)
            submissions.append(
                {
                    "id": uid,
                    "text": text,
                    "url": url,
                    "title": title,
                    "description": desc,
                    "vector": embedding
                }
            )
            documentVectors.append({
                "vectorId": uid,
            })
        # 存储三步走，同步到lance
        # 同步到文件系统
        # 同步到数据库。暂时不需要
        updateOrCreateTable(VECTOR_NAMESPACE, submissions)

        # 500chunk作为一个写入文件的单位，一般pdf才会用
        size = 500
        chunks = [vectors[i * size:(i + 1) * size] for i in range(math.ceil(len(vectors) / size))]
        storeVectorResult(chunks, url)

    return JsonResponse({"success": True})


# 搜索流程，通过向量搜索以及相关性限制，返回相关的文档
# 将相关的文档做为context发给gpt
@csrf_exempt
def vector_search(request):
    # 向量搜索
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            query_vector = create_embedding(query)
            embedding = query_vector.data[0].embedding
            context, score, source_documents = vectorSearch(VECTOR_NAMESPACE, embedding)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": "查询失败：" + str(e)})
    else:
        return JsonResponse({"success": False, "message": "请求方式错误"})


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


def my_view(request):
    # 获取客户端 IP 地址
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        # 如果有代理服务器或负载均衡器，IP 地址可能是逗号分隔的列表
        ip_address = ip_address.split(',')[0].strip()
    else:
        # 没有代理服务器时直接从 REMOTE_ADDR 获取
        ip_address = request.META.get('REMOTE_ADDR')

    # 打印客户端 IP 地址
    print(f"Client IP: {ip_address}")

    return JsonResponse({"success": False, "message": "请求方式错误"})