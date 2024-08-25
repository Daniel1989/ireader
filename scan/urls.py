from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('crawl/', include('crawl.urls')),
    path('rss/', include('user.urls')),
    path('ai/', include('aitask.urls')),
    path('kl/', include('knowledge.urls')),
    # path("ai-assistant/", include("django_ai_assistant.urls")),
]
