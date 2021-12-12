from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_name = models.CharField(max_length=200)
    user_regday = models.DateTimeField(default=timezone.now(), null=True)
    user_payedday = models.DateTimeField(null=True)
    user_isactive = models.BooleanField(default=True)

    def __str__(self):
        return self.user_name

class MyStocks(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default="dummy")
    stock_number = models.IntegerField(default=0)
