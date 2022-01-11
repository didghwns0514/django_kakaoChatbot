from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .form import UserCreationForm,UserChangeForm
from .models import User

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('name','email','is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None,{'fields':('name','email','password')}),
        ("Personal info",{'fields':('is_payedOn',)}),
        ("Permissions",{'fields':('is_admin',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','email','is_payedOn', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
#admin.site.unregister(Group)