from django.urls import path

from . import views

urlpatterns = [
    path('gen', views.generate, name='index'),
    path('ready', views.crawl_ready, name='ready'),
]
