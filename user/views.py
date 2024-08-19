import datetime
import json
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from aitask.models import AiTask, SummaryTask
from user.models import UserRss, RssEntry
from django.utils.timezone import now as timezone_now

import feedparser
import urllib.parse
import hashlib



def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@csrf_exempt
def add(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        client_id = req.get('clientId')
        title = req.get('title')
        source_type = req.get('type')
        url = req.get('url')
        if is_valid_url(url) is False:
            return JsonResponse({"success": False, "errorMsg": "订阅失败，请确认链接是否有效"}, safe=False)
        try:
            UserRss.objects.create(uid=client_id, title=title, url=url, source_type=source_type)
        except Exception as e:
            return JsonResponse({"success": False, "errorMsg": "订阅失败，请确认标题或者链接是否已存在"}, safe=False)
        return JsonResponse({"success": True}, safe=False)
    return JsonResponse({"success": False}, safe=False)


def query_rss(request):
    client_id = request.GET.get("clientId")
    source = request.GET.get("type")
    rss_list = UserRss.objects.filter(uid=client_id, source_type=source).order_by('-id')
    return JsonResponse(
        {"success": True, "data": [{"id": item.id, "title": item.title, "url": item.url} for item in rss_list]},
        safe=False)


@csrf_exempt
def delete_rss(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get("id")
        client_id = data.get("clientId")
        target = UserRss.objects.get(id=id, uid=client_id)
        try:
            target.delete()
        except Exception as e:
            return JsonResponse({"success": False, "errorMsg": "删除失败"}, safe=False)
    return JsonResponse({"success": True}, safe=False)


def parse_rss(request):
    id = request.GET.get("id")
    client_id = request.GET.get("clientId")
    feed_type = request.GET.get("type")
    target = UserRss.objects.get(id=id)
    feed_url = target.url

    today_entry_list = RssEntry.objects.filter(source=feed_url, created__gte=datetime.date.today().strftime('%Y-%m-%d'))
    news = []
    if len(today_entry_list) < 1:
        if feed_type == 'single':
            RssEntry.objects.create(title=target.title, link=target.url, source=target.url)
        else:
            feed = feedparser.parse(feed_url)
            RssEntry.objects.bulk_create([RssEntry(
                title=entry.title,
                link=entry.link,
                source=feed_url,
                created=timezone_now(),
                modified=timezone_now()
            ) for entry in feed.entries])

    entry_list = RssEntry.objects.filter(source=feed_url,
                                         created__gte=datetime.date.today().strftime('%Y-%m-%d')).order_by('created')
    for entry in entry_list:
        summary_tasks = SummaryTask.objects.filter(url=entry.link).order_by('-created')
        if summary_tasks:
            summary_task = summary_tasks[0]
            aitasks = AiTask.objects.filter(uid=client_id, target=summary_task.id)
            if aitasks:
                news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "aiSummary": summary_task.result,
                    "aiSummaryStatus": summary_task.status,
                    "source": summary_task.source
                })
            else:
                news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "aiSummary": '',
                    "aiSummaryStatus": ''
                })
        else:
            news.append({
                "title": entry.title,
                "link": entry.link,
                "aiSummary": '',
                "aiSummaryStatus": ''
            })
    return JsonResponse({"success": True, "data": news}, safe=False)


def generate_hash(input_string):
    today_str = timezone_now().strftime('%Y-%m-%d')
    salted_input = input_string + today_str
    hash_object = hashlib.sha256()
    hash_object.update(salted_input.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    return hash_hex

def init(request):
    token = request.GET.get('tokendt')
    if token is not None and len(token) > 3:
        response = HttpResponse("Cookie has been set.")
        cookie_value = generate_hash(token)
        response.set_cookie('tokendt', cookie_value, max_age=3600 * 24, httponly=True)  # Expires in 1 hour
        return response
    return HttpResponseForbidden("请登录")
