from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('list', views.page_list, name='list'),
    path('chat', views.chatgpt, name='chat'),
    path('ideas_crawl', views.generate_idea_from_hn, name='ideas'),
    path('ideas_list', views.show_ideas, name='show'),
    path('conversation/create/', views.create_conversation, name='create_conversation'),
    path('conversation/<int:conversation_id>/chat/', views.chat_with_history, name='chat_with_history'),
    path('conversation/<int:conversation_id>/history/', views.get_conversation_history, name='get_conversation_history'),
]
