from django.db import models
from django.utils import timezone
from appStockInfo.models import (
    StockTick,
    StockItem
)
# Create your models here.

class StockPrediction(models.Model):
    stock_item = models.ForeignKey(StockItem,
                                   on_delete=models.CASCADE,
                                   default="Dummy")
    prediction_percent = models.FloatField(default=0, null=False)

class StockPredictionHistory(models.Model):
    stock_tick = models.ForeignKey(StockTick,
                                   on_delete=models.CASCADE,
                                   default="Dummy")
    prediction_time = models.DateTimeField(default=timezone.now)
    value = models.FloatField(default=0, null=False)