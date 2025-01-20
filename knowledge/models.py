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
