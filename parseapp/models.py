from django.db import models

# Create your models here.
class StockListData(models.Model):

	source = models.CharField(max_length=100) # 코스피/코스닥
	# link = models.URLField()
	num = models.IntegerField()
	name = models.CharField(max_length=100)
	price_now = models.FloatField()
	price_compared = models.FloatField()
	price_ratio = models.FloatField()
	price_straight = models.FloatField()
	total_stock_sum = models.IntegerField()
	total_stock_num = models.IntegerField()
	total_foreign_ratio = models.FloatField()
	trade_sum = models.IntegerField()
	per = models.FloatField()
	roe = models.FloatField()

	class Meta:
		pass