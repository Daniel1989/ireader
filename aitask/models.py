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


class AiTask(CreationModificationDateMixin):
    uid = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    target = models.CharField(max_length=255)

    def __str__(self):
        return self.uid

    class Meta:
        verbose_name = 'ai任务'
        verbose_name_plural = 'ai任务'


class SummaryTask(CreationModificationDateMixin):
    url = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default='waiting')
    source = models.TextField(default='')
    result = models.TextField(default='')
    type = models.CharField(max_length=255, default='summarize')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = '新闻总结'
        verbose_name_plural = '新闻总结'
