from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('next', views.next_task, name='next'),
    path('finish', views.finish_task, name='finish'),
    path('waiting', views.query_waiting_list, name='waiting'),
]
