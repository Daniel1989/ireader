from django.urls import path

from . import views

urlpatterns = [
    path('goods', views.goods, name='goods'),
    path('market', views.market, name='market'),
    path('list', views.list, name='list'),
    path('edit', views.edit, name='edit'),
    path('goodslist', views.goodslist, name='goodslist'),
]
