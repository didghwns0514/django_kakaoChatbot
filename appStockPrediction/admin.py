from django.contrib import admin
from .models import StockPredictionHistory
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.
@admin.register(StockPredictionHistory)
class StockPredcitionAdmin(admin.ModelAdmin):
    list_display = ['stock_name', 'stock_tick',  'prediction', 'value', 'initial_close', 'prediction_time']
    search_fields = ['stock_name__stock_name', 'stock_tick__stock_tick']
    list_filter = ['prediction_time', ['prediction_time', DateRangeFilter], ['prediction_time', DateTimeRangeFilter]]

#admin.site.register(StockPredictionHistory, StockPredcitionAdmin)