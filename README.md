## Features

1. chrome plugins, send html to server
2. ask server analyze html, extract content, translate, summary, and create 3-5 tags
    1. 添加了celery， 需要在setting设置celery配置, 同时添加到celery的app名称（celery_reader）到install app中
    2. logger需要配置basicConfig且指定日志文件名
    3. celery 启动命令 celery -A celery_reader worker -l INFO
    4. 看起来celery启动的lancedb任务，没有权限写入文件夹，尽管已经设置文件夹权限为 777， 目前卡在db.tables_name()这个方法，后续再研究
3. embedding text
4. chat, search vector db, add to context, save chat history
5. based on tags, daily search and show related articles
6. 配置化，支持设置目标语言, 支持返回相似度多少的文案，支持接入llm

## how to deploy
1. 关闭之前的manage.py 和 celery进程
2. 启动manage.py (nohup python manage.py runserver 0.0.0.0:7860 &) 
3. 启动celery进程 (nohup celery -A celery_reader worker -l INFO &)
