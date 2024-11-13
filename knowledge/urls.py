from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('list', views.page_list, name='list'),
    path('parse', views.parse, name='parse'),
    path('ideas', views.generate_idea_from_hn, name='ideas'),
    path('ideas_show', views.show_ideas, name='show'),
    path('add_vector', views.create_vector, name='add_vector'),
    path('search', views.vector_search, name='vector_search'),
    path('chat', views.chatgpt, name='chat'),
]
