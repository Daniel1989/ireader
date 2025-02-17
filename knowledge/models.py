from django.db import models
from django.utils.timezone import now as timezone_now


class CreationModificationDateMixin(models.Model):
    created = models.DateTimeField("创建时间", editable=False)
    modified = models.DateTimeField("修改时间", editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone_now()
        else:
            if not self.created:
                self.created = timezone_now()
        self.modified = timezone_now()
        super(CreationModificationDateMixin, self).save(*args, **kwargs)

    save.alters_data = True

    class Meta:
        abstract = True


class MediumTextField(models.TextField):
    def db_type(self, connection):
        return 'MEDIUMTEXT'


class HtmlPage(CreationModificationDateMixin):
    class Status(models.TextChoices):
        WAIT_PROCESS = 'WAIT_PROCESS', '等待处理'
        PROCESSING = 'PROCESSING', '处理中'
        FINISH = 'FINISH', '处理完成'

    html = MediumTextField()
    text = MediumTextField(default="")
    target_language_text = MediumTextField(default="", verbose_name='目标语言文本')
    summary = models.TextField(default="")
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAIT_PROCESS,
        verbose_name='处理状态'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '网页知识点'
        verbose_name_plural = '网页知识点'

class HNIdeas(CreationModificationDateMixin):
    url = models.CharField(max_length=255)
    story_id = models.CharField(max_length=64)
    comment_id = models.CharField(max_length=64)
    summary = models.TextField()
    origin_text = MediumTextField(default="")

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'ideas'
        verbose_name_plural = 'ideas'

class Tag(models.Model):
    name = models.CharField(max_length=100)
    html_page = models.ForeignKey(HtmlPage, related_name='tags', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

class Vector(models.Model):
    html_page = models.ForeignKey(HtmlPage, related_name='vectors', on_delete=models.CASCADE)
    vector_id = models.UUIDField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vector {self.vector_id} for {self.html_page.title}"

    class Meta:
        verbose_name = '向量存储'
        verbose_name_plural = '向量存储'

class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键名')
    value = models.JSONField(verbose_name='配置值')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['-modified']  # Sort by last modified time

class Conversation(CreationModificationDateMixin):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', '进行中'
        ARCHIVED = 'ARCHIVED', '已归档'

    title = models.CharField(max_length=255, verbose_name='对话标题')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='状态'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '对话'
        verbose_name_plural = '对话'
        ordering = ['-modified']

class Message(CreationModificationDateMixin):
    class Role(models.TextChoices):
        USER = 'user', '用户'
        ASSISTANT = 'assistant', '助手'

    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name='所属对话'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name='发送者'
    )
    content = models.TextField(verbose_name='消息内容')
    references = models.JSONField(default=list, blank=True, verbose_name='引用来源')

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created']

class WebsiteCrawlRule(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    article_list_selector = models.CharField(max_length=255)  # CSS selector for article list
    article_link_selector = models.CharField(max_length=255)  # CSS selector for article links
    article_title_selector = models.CharField(max_length=255)  # CSS selector for article title
    article_content_selector = models.CharField(max_length=255)  # CSS selector for article content
    created = models.DateTimeField(default=timezone_now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain
