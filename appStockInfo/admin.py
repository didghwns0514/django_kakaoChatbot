from django.contrib import admin
from .models import StockItem
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.
@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['stock_name', 'stock_map_section', 'reg_date']
    search_fields = ['stock_name__stock_name']
    list_filter = [['reg_date', DateRangeFilter], ['reg_date', DateTimeRangeFilter]]

#admin.site.regis