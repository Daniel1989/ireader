from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('list', views.page_list, name='list'),
    path('parse', views.parse, name='parse'),
]
