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


class StockSection(models.Model):
    section_integer = models.AutoField(primary_key=True)
    section_name = models.CharField(max_length=200, blank=False, default="DummyName")

    def __str__(self):
        return self.section_name


class StockItemListSection(models.Model):
    stock_tick = models.ForeignKey(StockTick, on_delete=models.CASCADE, default="Dummy")
    section_name = models.ForeignKey(StockSection, on_delete=models.CASCADE, default="Dummy")
    total_sum = models.BigIntegerField(default=0)


class StockItem(models.Model):
    stock_name = models.ForeignKey(StockItemListName,
                                   on_delete=models.CASCADE, default="Dummy")
    stock_map_section = models.ForeignKey(StockItemListSection,
                                            on_delete=models.CASCADE,
                                            default="Dummy",
                                          )

    reg_date = models.DateField(default=timezone.now, null=True)

    open = models.FloatField(default=0.0)
    high = models.FloatField(default=0.0)
    low = models.FloatField(default=0.0)
    close = models.FloatField(default=0.0)
    volume = models.FloatField(default=0.0)


    """
    BPS : (주당순자산가치=청산가치): (순자산)/(총발행주식수)
    PER : (주가수익비율): (주가)/(주당순이익)
    EPS : (주당순이익): (당기순이익)/(총발행주식수)
    DIV : (배당수익률): (주가배당금/주가) * 100
    DPS : 주식배당금
    
    > roe : (당기순이익)/(자본총액) = EPS/BPS
    > roa : 
    """
    div = models.FloatField(default=0.0)

    per = models.FloatField(default=0.0) #
    pbr = models.FloatField(default=0.0) #
    roe = models.FloatField(default=0.0)
    #roa = models.FloatField(default=0.0)


class StockLastUpdateTime(models.Model):
    update_time = models.DateTimeField(default=timezone.now, null=False)