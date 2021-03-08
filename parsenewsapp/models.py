from django.db import models

# Create your models here.
class StockNewsData(models.Model):

	#url = models.URLField()
	url = models.TextField()
	title = models.CharField(max_length=100)
	article = models.TextField()
	timestamp = models.DateTimeField()

	def __str__(self):
		return self.title