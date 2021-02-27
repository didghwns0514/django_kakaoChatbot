from django.db import models
from config.settings import BASE_DIR, DATABASES
from datetime import datetime

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
	timestamp = models.DateTimeField()

	def save(self, *args, **kwargs):
		if not self.id:
			self.timestamp = datetime.utcnow()

		return super(StockListData, self).save(*args, **kwargs)

	# class Meta:
	# 	app_label = DATABASES['db_stock_list']['NAME']