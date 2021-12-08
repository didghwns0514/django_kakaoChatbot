from django.db import models
from django.utils import timezone


# Create your models here.
class StockUser(models.Model):
    user_name = models.CharField(max_length=200)

    def __str__(self):
        return self.user_name
