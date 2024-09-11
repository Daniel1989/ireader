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


class Goods(CreationModificationDateMixin):
    name = models.CharField(max_length=255, default='')
    date = models.DateField()
    currentTrending = models.CharField(max_length=255, default='')
    last5DaysTrending = models.CharField(max_length=255, default='')
    specialDaily = models.CharField(max_length=255, default='')
    currentBoxTop = models.CharField(max_length=255, default='')
    currentBoxBottom = models.CharField(max_length=255, default='')
    pcIndex = models.CharField(max_length=255, default='')
    cclTrending = models.CharField(max_length=255, default='')
    predictTrending = models.CharField(max_length=255, default='')
    predictTrendingReason = models.CharField(max_length=255, default='')
    stopLoss = models.CharField(max_length=255, default='')
    selectedGoodsInOtherMonth = models.CharField(max_length=255, default='')
    category = models.CharField(max_length=255, default='')
    categoryGoods = models.CharField(max_length=255, default='')
    whatIfAgainstTrending = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'date')




class Market(CreationModificationDateMixin):
    market = models.CharField(max_length=255, default='')
    date = models.DateField(unique=True)

    def __str__(self):
        return self.date

class GoodsItem(CreationModificationDateMixin):
    name = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name
