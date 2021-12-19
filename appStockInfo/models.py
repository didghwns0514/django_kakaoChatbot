from django.db import models
from django.utils import timezone

# Create your models here.

class StockTick(models.Model):
    stock_tick = models.CharField(primary_key=True, max_length=200)
    stock_marketName = models.CharField(max_length=200, blank=False)
    stock_isInfoAvailable = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.stock_tick


class StockItemListName(models.Model):
    stock_tick = models.ForeignKey(StockTick, on_delete=models.CASCADE, default="Dummy")
    stock_name = models.CharField(default="DummyName", max_length=200)

    def __str__(self):
        return self.stock_name

class StockItem(models.Model):
    stock_name = models.ForeignKey(StockItemListName,
                                   on_delete=models.CASCADE, default="Dummy")
    reg_date = models.DateField(default=timezone.now, null=True)
    high = models.FloatField(default=0.0)
    low = models.FloatField(default=0.0)
    open = models.FloatField(default=0.0)
    close = models.FloatField(default=0.0)
    volume = models.FloatField(default=0.0)

    total_sum = models.IntegerField(default=0)

    per = models.FloatField(default=0.0)
    pbr = models.FloatField(default=0.0)
    roe = models.FloatField(default=0.0)
    roa = models.FloatField(default=0.0)

class StockLastUpdateTime(models.Model):
    update_time = models.DateTimeField(default=timezone.now, null=False)