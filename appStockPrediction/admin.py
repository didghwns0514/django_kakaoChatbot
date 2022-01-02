from django.contrib import admin
from .models import StockPredictionHistory

# Register your models here.
class StockPredcitionAdmin(admin.ModelAdmin):
    list_display = ['stock_name', 'stock_tick', 'prediction_time', 'prediction_percent', 'value']
    search_fields = ['stock_name', 'stock_tick']

admin.site.register(StockPredictionHistory, StockPredcitionAdmin)