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
    html = MediumTextField()
    text = MediumTextField(default="")
    summary = models.TextField(default="")
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '网页知识点'
        verbose_name_plural = '网页知识点'
