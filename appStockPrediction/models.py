from django.db import models
from appStockInfo.models import (
    StockItem
)
# Create your models here.

class StockPrediction(models.Model):
    stock_item = models.ForeignKey(StockItem, default="Dummy")
    prediction_percent = models.FloatField(default=0, null=False)