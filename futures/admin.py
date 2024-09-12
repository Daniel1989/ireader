from django.contrib import admin
from .models import GoodsItem, Goods, Market
# Register your models here.
admin.site.register(GoodsItem)
admin.site.register(Goods)
admin.site.register(Market)