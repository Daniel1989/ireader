from django.urls import path

from . import views

urlpatterns = [
    path('add', views.add, name='add'),
    path('list', views.query_rss, name='list'),
    path('detail', views.parse_rss, name='parse'),
    path('delete', views.delete_rss, name='delete'),
]
