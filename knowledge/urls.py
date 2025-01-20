from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('list', views.page_list, name='list'),
    path('ideas', views.generate_idea_from_hn, name='ideas'),
    path('ideas_show', views.show_ideas, name='show'),
    path('chat', views.chatgpt, name='chat'),
]
