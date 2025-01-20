from django.contrib import admin
from .models import HtmlPage, HNIdeas, Tag, Vector, SystemConfig, Conversation, Message


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'modified', 'created')
    list_filter = ('modified', 'created')
    search_fields = ('key',)
    readonly_fields = ('created', 'modified')
    ordering = ('-modified',)

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of critical system configs
        return request.user.is_superuser


@admin.register(HtmlPage)
class HtmlPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'status', 'created', 'modified')
    list_filter = ('status', 'created', 'modified')
    search_fields = ('title', 'url')
    fields = ('title', 'url', 'html', 'text', 'target_language_text', 'summary', 'status', 'created', 'modified')
    readonly_fields = ('created', 'modified')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'html_page', 'created')
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    list_display = ('vector_id', 'html_page', 'created')
    list_filter = ('created',)
    search_fields = ('vector_id', 'html_page__title')


@admin.register(HNIdeas)
class HNIdeasAdmin(admin.ModelAdmin):
    list_display = ('url', 'story_id', 'comment_id', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('url', 'story_id', 'comment_id')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created', 'modified')
    list_filter = ('status', 'created', 'modified')
    search_fields = ('title',)
    readonly_fields = ('created', 'modified')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'content_preview', 'created')
    list_filter = ('role', 'created', 'conversation')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('created', 'modified')

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = '消息内容预览'
