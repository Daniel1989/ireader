import datetime

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db.models import Q

from aitask.models import SummaryTask, AiTask


# Create your views here.
@csrf_exempt
def create(requst):
    if requst.method == 'POST':
        data = json.loads(requst.body)
        url = data.get('url')
        client_id = data.get('clientId')
        created_task = AiTask.objects.filter(uid=client_id, type='summarize', created__gte=datetime.date.today().strftime('%Y-%m-%d'))
        if len(created_task) > 10:
            return JsonResponse({"success": False, "errorMsg": "您今日安排的AI阅读任务已达上限，请明日再来吧"})
        task = SummaryTask.objects.filter(url=url).exclude(status='failed')
        if not task:
            new_task = SummaryTask.objects.create(url=url)
            AiTask.objects.create(uid=client_id, type='summarize', target=new_task.id)
            # threading.Thread(target=exec_task, args=(new_task.id,'summarize')).start()
        else:
            task = task[0]
            AiTask.objects.create(uid=client_id, type='summarize', target=task.id)
    return JsonResponse({"success": True})


def next_task(request):
    task = SummaryTask.objects.filter(type='summarize', status='waiting').order_by('created')
    if task:
        task = task[0]
        task.status = 'starting'
        task.save()
        return JsonResponse({"success": True, "data": [{
            'id': task.id,
            'url': task.url
        }]})
    else:
        return JsonResponse({"success": False, "data": []})


@csrf_exempt
def finish_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("crawl result:", data)
        id = data.get('id')
        content = data.get('content')
        web = data.get('web')
        status = data.get('status')
        task = SummaryTask.objects.get(id=id)
        task.status = 'finish'
        task.result = content
        task.source = web
        task.status = status
        task.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


def query_waiting_list(request):
    uid = request.GET.get("clientId")
    aitask_list = AiTask.objects.filter(uid=uid)
    target_ids = [item.target for item in aitask_list]
    pending_summary_task = SummaryTask.objects.filter(status__in=['waiting'], id__in=target_ids).order_by('created')
    if pending_summary_task:
        first_task = pending_summary_task[0]
        before_summary_task = SummaryTask.objects.filter(status='waiting', created__lt=first_task.created)
        return JsonResponse({"success": True, "myWaitingTask": len(pending_summary_task), "beforeMyTask": len(before_summary_task)})
    else:
        return JsonResponse({"success": True, "myWaitingTask": 0})





