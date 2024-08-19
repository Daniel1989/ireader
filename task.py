import json
import os
import time

import requests
import torch
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import traceback
from openai import OpenAI

load_dotenv()

prompt = '''
# 角色
你是一个专业的 Google 爬虫，能够精准且高效地从给定网页的 HTML 代码中提取出核心主要内容。

## 技能
### 技能 1: 内容提取
1. 仔细分析网页的 HTML 结构和元素。
2. 准确识别并提取出标题、正文、重要段落、关键图片描述等主要内容。
3. 忽略广告、侧边栏等无关信息。回复示例：
=====
   <提取出的网页正文主要内容>
=====

## 限制:
- 只提取与网页主题相关的重要内容，排除无关干扰。
- 严格按照给定的格式进行输出，不得随意更改。
- 提取的内容应准确反映网页的核心要义。
- 只需要输出提取的正文，不要输出其他内容
- 保持原文的语言，不要翻译

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


def crawl(url):
    with sync_playwright() as p:
        target = p.chromium
        content = None
        for browser_type in [target]:  # p.firefox, p.chromium, p.webkit
            browser = browser_type.launch()
            try:
                page = browser.new_page()
                page.goto(url)
                page.wait_for_selector("body")
                content = page.content()
                content = clearup(content)
                browser.close()
            except Exception as e:
                print("error in playwright", e)
                traceback.print_exc()
                browser.close()
    if content is not None:
        # print("获取的html内容：", content)
        # web = summary(prompt + "\n" + content)
        # print(content)
        web = summary_api(prompt + "\n" + content)
        result = summary(
            "根据下文输出一段500字以内的中文总结，待总结的内容是：" + web + "\n, 注意：只需要输出最后总结的内容，不要输出其他内容")
        return web, result
    return '', ''


def query(payload):
    API_URL = "https://ai.gitee.com/api/inference/serverless/KGHCVOPBV7GY/chat/completions"
    headers = {
        "Authorization": "Bearer " + os.environ["SERVERLESS_API_KEY"],
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.encoding = 'utf-8'
    return json.loads(response.text)


def summary_api(content):
    # output = query({
    #     "messages": [
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": content}
    #     ],
    #     "stream": False,
    #     "max_tokens": 50000,
    #     "temperature": 0.7,
    #     "top_p": 0.7,
    #     "top_k": 50
    # })
    # result = output["choices"][0]["message"]["content"]
    # return result
    client = OpenAI(
        base_url=os.environ["BASE_URL"],
        api_key=os.environ["SERVERLESS_API_KEY"],
    )
    completion = client.chat.completions.create(
        model=os.environ["MODEL_NAME"],
        temperature=0.7,
        stream=False,
        top_p=0.8,
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content


def summary(content):
    base_url = os.environ["BASE_URL"]
    api_key = os.environ["SERVERLESS_API_KEY"]
    model_name = os.environ["MODEL_NAME"]
    print("summary model_name", model_name)
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model=model_name,
        temperature=0.7,
        stream=False,
        top_p=0.8,
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    host = "http://127.0.0.1:7860"
    while True:
        try:
            data = requests.get(f"{host}/crawl/ready")
            data = data.json()
            if data["ready"]:
                print(":) playwright is ready")
                break
            else:
                time.sleep(5)
                print(":( playwright is not ready")
        except Exception as e:
            time.sleep(5)
            print("error in check playwright: ", e)
    while True:
        try:
            start_time = time.time()
            next_task = requests.get(f"{host}/ai/next")
            next_task = next_task.json()
            print(next_task)
            if len(next_task["data"]) == 0:
                print("no more task")
                time.sleep(5)
                continue
            next_task = next_task["data"][0]
            url = next_task["url"]
            try:
                web, content = crawl(url)
                if len(content) < 10:
                    raise Exception("content is too short")
                requests.post(f"{host}/ai/finish", json={"id": next_task["id"], "web": web, "content": content, "status": "finish"})
                end_time = time.time()
                print("task cost time in seconds:", end_time - start_time)
            except Exception as e:
                requests.post(f"{host}/ai/finish", json={"id": next_task["id"], "content": "", "web": "", "status": "failed"})
                traceback.print_exc()
                print("error in do task: ", e)
        except Exception as e:
            print("error in loop: ", e)
        time.sleep(5)
