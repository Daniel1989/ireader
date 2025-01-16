import json
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import uuid

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
    for chunk in client.chat.completions.create(
            model=model_name,
            temperature=0.7,
            stream=True,
            top_p=0.8,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ]
    ):
        res = chunk.choices[0].delta.content
        if chunk.choices[0].finish_reason == 'stop':
            data = json.dumps(dict(textResponse=res, uuid=chunk.id, sources=[], type='finalizeResponseStream', close=True, error=False), ensure_ascii=False)
        else:
            data = json.dumps(dict(textResponse=res, uuid=chunk.id, sources=[], type='textResponseChunk', close=False, error=False), ensure_ascii=False)
        yield f'data: {data}\n\n'


def exact(html):
    content = clearup(html)
    web = chat(prompt + "\n" + content)
    return web


def summary(content):
    result = chat(
        "根据下文输出一段500字以内的中文总结，待总结的内容是：" + content + "\n, 注意：只需要输出最后总结的内容，不要输出其他内容")
    return result


# TODO 使用embedding

def create_embedding(text):
    model_name = os.environ["EMBEDDING_MODEL_NAME"]
    response = client.embeddings.create(input=[str(text)], model=model_name)
    return response
