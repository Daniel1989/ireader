import time

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from knowledge.llm import exact, summary
from knowledge.models import HtmlPage


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
    pages = HtmlPage.objects.all().order_by('-created')
    data = [{
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "text": item.text,
        "summary": item.summary,
        "created": item.created
    } for item in pages]
    return JsonResponse({"success": True, "data": data})


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
