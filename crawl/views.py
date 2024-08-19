import json
import threading
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Create your views here.
# from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from crawl.models import CrawlLog


def request_llm(text):
    # data = requests.post("http://127.0.0.1:8000/api/predict", json={"data": [text]})
    # return json.loads(data.text)["data"][0]
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="empty",
    )
    completion = client.chat.completions.create(
        model="Qwen/Qwen2-1.5B-Instruct-AWQ",
        temperature=0.7,
        top_p=0.8,
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content


# def index(request):
#     context = {
#         'title': 'Welcome to My Website',
#         'message': 'Hello, this is a message from the view!',
#         'items': ['Item 1', 'Item 2', 'Item 3']
#     }
#     return render(request, 'index.html', context)

def crawl_ready(request):
    try:
        price_detail = []
        with sync_playwright() as p:
            target = p.chromium
            for browser_type in [target]:  # p.firefox, p.chromium, p.webkit
                browser = browser_type.launch()
                try:
                    page = browser.new_page()
                    page.goto('https://finance.sina.com.cn/futures/quotes/AG2412.shtml')
                    page.wait_for_selector(".min-price")
                    content = page.evaluate("""
                                () => {
                          return document.getElementById("table-box-futures-hq").innerHTML
                        }
                                """)
                    soup = BeautifulSoup('<div>' + content + '</div>', 'html.parser')
                    trs = soup.find_all("tr")
                    for index, tr in enumerate(trs):
                        td = tr.find_all("td")
                        if index == 3:
                            continue
                        else:
                            if index == 0:
                                first = td.pop(0)
                                trade_time = first.find(class_='trade-time').text
                                current_price = first.find(class_='price').text
                                price_diff = first.find(class_='amt-value').text.replace("+", "").replace("-", "")
                                price_diff_percent = first.find(class_='amt').text.replace("+", "") \
                                    .replace("-", "").replace("%", "")
                                price_detail.append(trade_time)
                                price_detail.append(current_price)
                                price_detail.append(price_diff)
                                price_detail.append(price_diff_percent)
                                print("crawl data is ", price_detail)
                    browser.close()
                except Exception as e:
                    browser.close()
                    print("parse page error", e)
        is_ready = len(price_detail) == 4
        return JsonResponse({"success": True, "data": price_detail, "ready": is_ready}, safe=False)
    except Exception as e:
        return JsonResponse({"success": True, "data": [], "ready": False}, safe=False)



@csrf_exempt
def generate(request):
    if request.method == 'POST':
        CrawlLog.objects.create(url="http://www.baidu.cn")
        data = json.loads(request.body)
        prompt = data.get('prompt')
        threading.Thread(target=request_llm, args=(prompt,)).start()
        logs = CrawlLog.objects.all()
        return JsonResponse({"success": True, "data": "start call", "logs": [item.url for item in logs]}, safe=False)
    return JsonResponse({"success": False}, safe=False)

