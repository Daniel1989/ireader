## Features

1. chrome plugins, send html to server
2. ask server analyze html, extract content, translate, summary, and create 3-5 tags
    1. 添加了celery， 需要在setting设置celery配置, 同时添加到celery的app名称（celery_reader）到install app中
    2. logger需要配置basicConfig且指定日志文件名
3. embedding text
4. chat, search vector db, add to context, save chat hhistory
5. based on tags, daily search and show related articles