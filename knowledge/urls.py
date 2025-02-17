from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('list', views.page_list, name='list'),
    path('ideas_crawl', views.generate_idea_from_hn, name='ideas'),
    path('ideas_list', views.show_ideas, name='show'),
    path('conversation/create', views.create_conversation, name='create_conversation'),
    path('conversation/<int:conversation_id>/chat', views.chat_with_history, name='chat_with_history'),
    path('conversation/<int:conversation_id>/history', views.get_conversation_history, name='get_conversation_history'),
    path('init', views.init, name='init'),
    path('conversations', views.get_conversations, name='get_conversations'),
    path('tags/stats', views.get_tag_stats, name='tag_stats'),
    path('tags/persona', views.generate_persona, name='generate_persona'),
    path('tags/recommendations', views.generate_recommendations, name='generate_recommendations'),
    path('tags/persona-with-recommendations', views.generate_persona_with_recommendations, name='generate_persona_with_recommendations'),
    path('website/analyze', views.analyze_website_articles, name='analyze_website_articles'),
    path('translate', views.translate, name='translate'),
]
