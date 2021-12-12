from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'user_name', 'user_regday', 'user_payedday', 'user_isactive']
    list_editable = ['user_isactive']
    search_fields = ['user_id', 'user_name', 'user_payedday']

admin.site.register(User, UserAdmin)