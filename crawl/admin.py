from django.contrib import admin
from .models import CrawlLog


class CrawlLogAdmin(admin.ModelAdmin):
    list_display = ('url',)


# Register your models here
admin.site.register(CrawlLog, CrawlLogAdmin)
