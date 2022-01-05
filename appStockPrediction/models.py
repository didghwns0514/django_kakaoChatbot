from django.db import models
from django.utils import timezone
from appStockInfo.models import (
    StockTick,
    StockItem, StockItemListName
)
# Create your models here.

class StockPredictionHistory(models.Model):
    stock_name = models.ForeignKey(StockItemListName,
                                   on_delete=models.CASCADE,
                                   default="Dummy")
    stock_tick = models.ForeignKey(StockTick,
                                   on_delete=models.CASCADE,
                                   default="Dummy")
    prediction_time = models.DateTimeField(default=timezone.now, null=False)
    prediction_percent = models.FloatField(default=0, null=False)
    initial_close = models.FloatField(default=0, null=False)
    value = models.FloatField(default=0, null=False)

    def __str__(self):
        return self.stock_name.stock_name